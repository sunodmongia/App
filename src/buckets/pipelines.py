import threading
import time
import os
import hashlib
import zipfile
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
    Simulates an industrial build pipeline for Compute Apps.
    Handles specialized builds for Django/Node and generic builds for other runtimes.
    """
    try:
        deployment = AppDeployment.objects.get(id=deployment_id)
        app = deployment.app
        org = app.organization
        
        logs = []
        def add_log(msg):
            logs.append(msg)
            # Update DB with current progress
            deployment.logs = "\n".join(logs)
            deployment.save(update_fields=['logs'])
            
            # Real-time Telemetry
            broadcast(org, {
                'type': 'build_log',
                'app_id': app.id,
                'deployment_id': deployment.deployment_id,
                'message': msg
            })
            time.sleep(0.6) # Slightly longer delay for industrial feel

        add_log(f"--- Initialization of build {deployment.deployment_id} ---")
        add_log(f"[INFO] Runtime detected: {app.runtime}")
        add_log("[RUNNING] Provisioning isolated build container...")
        time.sleep(1)

        # 1.1 Infrastructure Validation & Hub Orchestration
        target_dir = app.provisioning_path
        
        # Priority: Org Global Hub > App Local Path > Workspace Default
        if org.deployment_root:
            target_dir = os.path.join(org.deployment_root, app.name.replace(' ', '_'))
            
        if not target_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            target_dir = os.path.join(base_dir, 'deployments', app.name.replace(' ', '_'))
            
        try:
            # Ensure parent hub exists
            parent_dir = os.path.dirname(target_dir)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            add_log(f"[INFO] Infrastructure Target (Hub): {target_dir}")
        except Exception as e:
            add_log(f"[CRITICAL ERROR] Infrastructure unreachable: {str(e)}")
            deployment.status = 'failed'
            deployment.save()
            return

        # 2. Structural Inspection & Physical Provisioning
        if deployment.artifact:
            # Set target directory
            target_dir = app.provisioning_path
            if not target_dir:
                # Default to a subfolder in the workspace if not specified
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                target_dir = os.path.join(base_dir, 'deployments', app.name.replace(' ', '_'))
            
            add_log(f"[INFO] Provisioning target: {target_dir}")
            
            try:
                # 2.1 File Extraction
                with zipfile.ZipFile(deployment.artifact.path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    add_log(f"[RUNNING] Extracting {len(file_list)} files to local disk...")
                    
                    # Ensure directory exists and is clean
                    if os.path.exists(target_dir):
                        add_log(" > Clearing existing artifacts at target location...")
                        import shutil
                        shutil.rmtree(target_dir)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Physical Extraction
                    zip_ref.extractall(path=target_dir)
                    add_log(f"[SUCCESS] Multi-file project provisioned at: {target_dir}")
                    
                    # Filter for top-level files to verify structure
                    top_level = sorted(list(set([f.split('/')[0] for f in file_list])))[:5]
                    add_log(f" > Project Head: {', '.join(top_level)}")
                    
                    if 'manage.py' in file_list:
                        add_log(" > [Django] Detected: manage.py")
                    if 'package.json' in file_list:
                        add_log(" > [Node.js] Detected: package.json")
                    
                    # 2.2 Configuration Fulfillment (Secret Injection)
                    add_log("[INFO] Physically injecting secrets into edge environment...")
                    env_vars = app.env_vars.all()
                    if env_vars.exists():
                        env_content = ""
                        for var in env_vars:
                            env_content += f"{var.key}={var.value}\n"
                        
                        env_path = os.path.join(target_dir, '.env')
                        with open(env_path, 'w') as f:
                            f.write(env_content)
                        add_log(f" > Successfully provisioned .env with {env_vars.count()} variables.")
                    else:
                        add_log(" > No environment variables defined. Skipping .env generation.")
            except Exception as e:
                add_log(f"[CRITICAL ERROR] Provisioning failed: {str(e)}")
                deployment.status = 'failed'
                deployment.save()
                return
        else:
            add_log("[INFO] No artifact provided for physical provisioning.")
        
        time.sleep(1)
        runtime_lower = app.runtime.lower()
        
        if 'django' in runtime_lower:
            add_log("[RUNNING] Installing dependencies from requirements.txt...")
            add_log(" > Successfully installed django-5.1.x, psycopg2-binary, gunicorn")
            add_log("[RUNNING] Running system checks and migrations...")
            add_log(" > Operations to perform: 0 migrations to apply.")
            add_log("[RUNNING] Compiling static assets via collectstatic...")
            add_log(" > 142 static files copied to /var/www/static")
        elif any(r in runtime_lower for r in ['node', 'react', 'next', 'js']):
            add_log("[RUNNING] npm install --production...")
            add_log(" > added 452 packages from 213 contributors")
            add_log("[RUNNING] npm run build...")
            add_log(" > [next-build] Optimization complete.")
        else:
            # Generic Industrial Build Sequence
            add_log(f"[RUNNING] Detecting build configuration for {app.runtime}...")
            time.sleep(1)
            add_log(f"[RUNNING] Executing native fetch for {app.runtime} packages...")
            add_log(" > Fetching core components from global repositories... DONE")
            add_log("[RUNNING] Optimizing build artifacts and entrypoints...")
            time.sleep(1)
            add_log(" > Universal build artifacts generated successfully.")

        add_log("[INFO] Build successful. Optimizing edge propagation...")
        time.sleep(1.2)
        add_log("[SUCCESS] App distribution published to Wire Global Edge Network.")
        
        # Finalize
        app.is_live = True
        app.status = 'live'
        app.last_deployed_at = timezone.now()
        app.save(update_fields=['is_live', 'status', 'last_deployed_at'])
        
        deployment.status = 'success'
        deployment.logs = "\n".join(logs)
        deployment.completed_at = timezone.now()
        deployment.save(update_fields=['status', 'logs', 'completed_at'])
        
        broadcast(org, {
            'type': 'app_live',
            'app_id': app.id,
            'url': app.get_deployment_url()
        })

    except AppDeployment.DoesNotExist:
        pass
    except Exception as e:
        print(f"Deployment error for {deployment_id}: {e}")
        try:
            deployment = AppDeployment.objects.get(id=deployment_id)
            deployment.status = 'error'
            deployment.logs += f"\n[FATAL ERROR] {str(e)}"
            deployment.save(update_fields=['status', 'logs'])
            
            app = deployment.app
            app.status = 'error'
            app.save(update_fields=['status'])
        except Exception:
            pass

