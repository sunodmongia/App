import threading
import time
import os
import hashlib
import zipfile
import subprocess
import signal
import sys

from PIL import Image
from pypdf import PdfReader
from django.utils.timezone import now
from django.utils import timezone
from saas.consumers import broadcast
from .models import FileObject, AppDeployment

def start_processing_pipeline(file_object_id):
    """Entry point for the background pipeline."""
    thread = threading.Thread(target=process_file_async, args=(file_object_id,))
    thread.daemon = True
    thread.start()

def process_file_async(file_id):
    """Simulates a real-time object processing pipeline."""
    # Small delay to simulate network/queue lag
    time.sleep(2)
    
    try:
        file_obj = FileObject.objects.get(id=file_id)
        file_obj.status = 'processing'
        file_obj.save(update_fields=['status'])
        
        # 1. Integrity Check (Checksum)
        sha256 = hashlib.sha256()
        with file_obj.file.open('rb') as f:
            for chunk in f.chunks():
                sha256.update(chunk)
        file_obj.checksum = sha256.hexdigest()
        
        # 2. Metadata Extraction
        metadata = file_obj.metadata or {}
        metadata['processed_at'] = now().isoformat()
        
        content_type = file_obj.content_type
        
        if 'image' in content_type:
            try:
                with Image.open(file_obj.file) as img:
                    metadata['dimensions'] = f"{img.width}x{img.height}"
                    metadata['format'] = img.format
                    metadata['mode'] = img.mode
            except Exception as e:
                metadata['extraction_error'] = str(e)
                
        elif 'pdf' in content_type:
            try:
                reader = PdfReader(file_obj.file)
                metadata['pages'] = len(reader.pages)
                if reader.metadata:
                    metadata['author'] = reader.metadata.get('/Author', 'Unknown')
                    metadata['producer'] = reader.metadata.get('/Producer', 'Unknown')
            except Exception as e:
                metadata['extraction_error'] = str(e)

        file_obj.metadata = metadata
        file_obj.status = 'ready'
        file_obj.save(update_fields=['checksum', 'metadata', 'status', 'updated_at'])
        
        # Broadcast via Channel if needed (can add later)
        
    except FileObject.DoesNotExist:
        pass
    except Exception as e:
        print(f"Pipeline error for file {file_id}: {e}")
        try:
            file_obj = FileObject.objects.get(id=file_id)
            file_obj.status = 'error'
            file_obj.metadata['error'] = str(e)
            file_obj.save(update_fields=['status', 'metadata'])
        except FileObject.DoesNotExist:
            pass

def start_app_deployment_pipeline(deployment_id):
    """Entry point for the App Deployment/Build pipeline."""
    thread = threading.Thread(target=run_app_build_async, args=(deployment_id,))
    thread.daemon = True
    thread.start()

def run_app_build_async(deployment_id):
    """
    Industrial automated build pipeline for Compute Apps.
    Handles extraction, secret injection, and real-time process execution.
    """
    try:
        deployment = AppDeployment.objects.get(id=deployment_id)
        app = deployment.app
        org = app.organization
        
        logs = []
        def add_log(msg):
            logs.append(msg)
            deployment.logs = "\n".join(logs)
            deployment.save(update_fields=['logs'])
            broadcast(org, {
                'type': 'build_log',
                'app_id': app.id,
                'deployment_id': deployment.deployment_id,
                'message': msg
            })
            time.sleep(0.4)

        add_log(f"--- Initialization of Automated Build {deployment.deployment_id} ---")
        add_log(f"[INFO] Stack Detected: {app.runtime}")

        # 1. Infrastructure Preparation
        target_dir = app.provisioning_path
        if org.deployment_root:
            target_dir = os.path.join(org.deployment_root, app.name.replace(' ', '_'))
        if not target_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            target_dir = os.path.join(base_dir, 'deployments', app.name.replace(' ', '_'))
            
        add_log(f"[INFO] Infrastructure Target: {target_dir}")
        
        # 2. Physical Provisioning
        if not deployment.artifact:
            raise Exception("No deployment artifact provided.")
            
        parent_dir = os.path.dirname(target_dir)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        if os.path.exists(target_dir):
            add_log(" > Clearing existing artifacts at target location...")
            import shutil
            shutil.rmtree(target_dir, ignore_errors=True)
        os.makedirs(target_dir, exist_ok=True)

        with zipfile.ZipFile(deployment.artifact.path, 'r') as zip_ref:
            add_log(f"[RUNNING] Physically extracting {len(zip_ref.namelist())} artifacts...")
            zip_ref.extractall(path=target_dir)
            add_log("[SUCCESS] Physical infrastructure provisioned successfully.")

        # 3. Configuration Fulfillment (Secret Projection)
        env_vars = app.env_vars.all()
        if env_vars.exists():
            add_log(f"[INFO] Projecting {env_vars.count()} secrets into local environment...")
            env_content = "\n".join([f"{v.key}={v.value}" for v in env_vars])
            with open(os.path.join(target_dir, '.env'), 'w') as f:
                f.write(env_content)
            add_log(" > Successfully provisioned .env file.")

        # 4. AWS-Grade Automated Execution
        add_log("[INFO] Orchestrating automated project launch...")
        success, msg = launch_edge_node(app, add_log)
        
        if success:
            add_log(f"[SUCCESS] {msg}")
            app.status = 'live'
            app.is_live = True
            app.last_deployed_at = timezone.now()
            app.save(update_fields=['status', 'is_live', 'last_deployed_at'])
            
            deployment.status = 'live'
            deployment.save(update_fields=['status'])
            
            # Final Success Broadcast
            broadcast(org, {
                'type': 'app_live',
                'app_id': app.id,
                'port': app.active_port,
                'url': f"http://127.0.0.1:{app.active_port}"
            })
            add_log("--- Deployment Lifecycle Finalized ---")
        else:
            raise Exception(f"Orchestration Engine failed: {msg}")

    except Exception as e:
        msg = f"[CRITICAL SYSTEM FAILURE] {str(e)}"
        try:
            deployment = AppDeployment.objects.get(id=deployment_id)
            deployment.status = 'failed'
            deployment.logs += f"\n{msg}"
            deployment.save()
            
            app = deployment.app
            app.status = 'failed'
            app.save()
            
            broadcast(app.organization, {
                'type': 'build_log',
                'app_id': app.id,
                'message': f"<span class='text-red-500 font-bold'>{msg}</span>"
            })
        except Exception as e:
            print(f"Orchestrator Error: {msg}")

def map_local_files(path):
    """Recursively map the directory structure for the UI explorer."""
    if not os.path.exists(path): 
        return []
    try:
        structure = []
        for item in os.listdir(path):
            ipath = os.path.join(path, item)
            is_dir = os.path.isdir(ipath)
            entry = {'name': item, 'type': 'directory' if is_dir else 'file'}
            if is_dir: 
                entry['children'] = map_local_files(ipath)
            structure.append(entry)
        return sorted(structure, key=lambda x: (x['type'] != 'directory', x['name']))
    except Exception as e:
        print(f"Error mapping files: {e}")
        return []

def launch_edge_node(app, logger=None):
    """AWS-Grade Execution: Detects stack and launches background process with log streaming."""
    target_path = app.provisioning_path
    if not target_path or not os.path.exists(target_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_path = os.path.join(base_dir, 'deployments', app.name.replace(' ', '_'))
    
    if not os.path.exists(target_path):
        return False, "Infrastructure not found."

    def log(m):
        if logger: 
            logger(m)

    # Port Strategy: Industrial Dynamic Assignment
    import socket
    def find_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    port = find_port()
    files = os.listdir(target_path)
    cmd = None

    if 'manage.py' in files:
        cmd = [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload']
    elif 'package.json' in files:
        cmd = ['npm', 'start']
    
    if not cmd:
        return False, "Runtime entrypoint (manage.py/package.json) not detected."

    try:
        process = subprocess.Popen(
            cmd, cwd=target_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, shell=True if os.name == 'nt' else False, bufsize=1, universal_newlines=True
        )
        app.process_pid = process.pid
        app.active_port = port
        app.save()

        # Telemetry Stream Thread
        def stream():
            log(f"[SYSTEM] Connection established to process {process.pid}")
            for line in iter(process.stdout.readline, ''):
                if line: 
                    log(f"[APP-LOG] {line.strip()}")
            process.stdout.close()
        
        threading.Thread(target=stream, daemon=True).start()
        return True, f"Edge Instance provisioned at http://127.0.0.1:{port}"
    except Exception as e:
        return False, str(e)

def terminate_edge_node(app):
    """Safely terminates the local infrastructure process."""
    if not app.process_pid: 
        return True, "No active process."
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(app.process_pid)], capture_output=True)
        else:
            os.kill(app.process_pid, signal.SIGTERM)
        app.process_pid = None
        app.status = 'stopped'
        app.save()
        return True, "Infrastructure node successfully decommissioned."
    except Exception as e:
        return False, str(e)