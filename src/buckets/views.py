import mimetypes
from django.db import models
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, FileResponse, HttpResponse, Http404
from django.contrib import messages
from django.utils.timezone import now

from saas.models import Usage
from saas.events import log_event
from saas.consumers import broadcast
from subscriptions.services import get_user_organization
from .models import Bucket, FileObject, StorageKey, App, AppDeployment
from .pipelines import start_processing_pipeline, start_app_deployment_pipeline

def get_org_storage_limit(org):
    """Returns the effective storage limit in MB for an organization."""
    if org.subscription and hasattr(org.subscription, 'planlimit'):
        return org.subscription.planlimit.storage_mb
    
    # Fallback to absolute default (1GB) if no plan limit found
    return 1024

class BucketMixin(LoginRequiredMixin):
    def get_organization(self):
        return get_user_organization(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        self.org = self.get_organization()
        if not self.org:
            messages.error(request, "You must be part of an organization to access storage.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

class BucketListView(BucketMixin, ListView):
    model = Bucket
    template_name = 'buckets/list.html'
    context_object_name = 'buckets'

    def get_queryset(self):
        return Bucket.objects.filter(organization=self.org)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate total ACTUAL usage (files)
        usage_record, _ = Usage.objects.get_or_create(user=self.org.owner)
        context['active_usage_mb'] = usage_record.storage_mb
        
        # Calculate RESERVED allocation (quotas)
        total_allocated = self.get_queryset().aggregate(models.Sum('quota_mb'))['quota_mb__sum'] or 0
        context['total_allocated_mb'] = total_allocated
        context['total_allocated_gb'] = round(total_allocated / 1024, 1)
        
        # Get plan limit
        limit = get_org_storage_limit(self.org)
        context['storage_limit_mb'] = limit
        context['plan_name'] = self.org.subscription.name if self.org.subscription else "Free"
        
        # Deployment stats
        context['total_live_deployments'] = self.get_queryset().filter(is_live=True).count()
        
        # Human readable display
        if limit >= 1024:
            context['storage_limit_display'] = f"{limit // 1024} GB"
        else:
            context['storage_limit_display'] = f"{limit} MB"
            
        # Dash offset based on ALLOCATION (Reserved Space)
        if limit > 0:
            context['allocation_percent'] = min(round((total_allocated / limit) * 100, 1), 100)
        else:
            context['allocation_percent'] = 0
            
        # Remaining for NEW allocations
        context['remaining_storage_mb'] = max(0, limit - total_allocated)
        context['remaining_storage_gb'] = round(context['remaining_storage_mb'] / 1024, 1)
            
        return context

class BucketCreateView(BucketMixin, View):
    def post(self, request, *args, **kwargs):
        name = slugify(request.POST.get('name', ''))
        quota_mb = int(request.POST.get('quota_mb', 1024))
        
        if not name:
            messages.error(request, "A valid bucket name (alphanumeric/hyphen) is required.")
            return redirect('buckets:list')
            
        # [Reserved Allocation Check]
        org_limit = get_org_storage_limit(self.org)
        current_allocated = Bucket.objects.filter(organization=self.org).aggregate(models.Sum('quota_mb'))['quota_mb__sum'] or 0
        
        if (current_allocated + quota_mb) > org_limit:
            messages.error(request, f"Over-allocation error. Only {max(0, (org_limit - current_allocated)/1024):.1f} GB remaining in your plan.")
            return redirect('buckets:list')
        
        bucket, created = Bucket.objects.get_or_create(
            name=name,
            organization=self.org,
            defaults={'quota_mb': quota_mb}
        )
        if created:
            log_event(self.org, "bucket_created", name=name)
            # Real-time Broadcast
            broadcast(self.org, {
                'type': 'bucket_created',
                'org_name': self.org.name,
                'name': name,
                'storage_update': {
                    'bucket_id': bucket.id,
                    'usage_mb': bucket.usage_mb,
                    'percent': bucket.usage_percent,
                    'quota_mb': bucket.quota_mb
                }
            })
            messages.success(request, f"Bucket '{name}' created successfully.")
        else:
            messages.warning(request, f"Bucket '{name}' already exists.")
            
        return redirect('buckets:detail', bucket_name=bucket.name)

class BucketDetailView(BucketMixin, DetailView):
    model = Bucket
    template_name = 'buckets/detail.html'
    context_object_name = 'bucket'
    slug_field = 'name'
    slug_url_kwarg = 'bucket_name'

    def get_queryset(self):
        return Bucket.objects.filter(organization=self.org)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = self.object.files.all()
        # Infrastructure Governance
        context['total_used_mb'] = self.org.get_total_usage_mb()
        context['plan_limit_mb'] = get_org_storage_limit(self.org)
        context['remaining_mb'] = max(0, context['plan_limit_mb'] - context['total_used_mb'])
        return context

class FileUploadView(BucketMixin, View):
    def post(self, request, bucket_name):
        bucket = get_object_or_404(Bucket, name=bucket_name, organization=self.org)
        files = request.FILES.getlist('files')
        
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)

        # 1. Check Global Organization Quota
        usage_record, _ = Usage.objects.get_or_create(user=self.org.owner)
        global_limit_mb = get_org_storage_limit(self.org)
        total_new_mb = sum(f.size for f in files) / (1024 * 1024)
        
        if (usage_record.storage_mb + total_new_mb) > global_limit_mb:
            return JsonResponse({
                'error': f'Organization storage limit exceeded ({global_limit_mb} MB total).'
            }, status=403)

        # 2. Check Individual Bucket Allocation
        bucket_usage = bucket.usage_mb
        if (bucket_usage + total_new_mb) > bucket.quota_mb:
            return JsonResponse({
                'error': f'Bucket allocation full ({bucket.quota_mb} MB). Increase allocation to store more.'
            }, status=403)

        uploaded_files = []
        for f in files:
            file_obj = FileObject.objects.create(
                bucket=bucket,
                file=f,
                name=f.name,
                size=f.size,
                content_type=f.content_type or mimetypes.guess_type(f.name)[0] or 'application/octet-stream',
                status='processing'
            )
            # Trigger real-time background processing
            start_processing_pipeline(file_obj.id)
            
            uploaded_files.append({
                'id': file_obj.id, 
                'name': file_obj.name,
                'status': 'processing'
            })
            
            # Update usage
            usage_record.storage_mb += (f.size / (1024 * 1024))
            usage_record.save()
            
            # Log event
            log_event(self.org, "file_uploaded", bucket=bucket.name, filename=f.name, size=f.size)
            
            # Real-time Broadcast
            broadcast(self.org, {
                'type': 'file_uploaded',
                'org_name': self.org.name,
                'name': f.name,
                'size': f.size,
                'bucket': bucket.name,
                'storage_update': {
                    'bucket_id': bucket.id,
                    'usage_mb': bucket.usage_mb,
                    'percent': bucket.usage_percent,
                    'quota_mb': bucket.quota_mb,
                    'total_org_usage_mb': usage_record.storage_mb
                }
            })

        return JsonResponse({'status': 'ok', 'files': uploaded_files})

class FileDownloadView(BucketMixin, View):
    def get(self, request, file_id):
        file_obj = get_object_or_404(FileObject, id=file_id, bucket__organization=self.org)
        return FileResponse(file_obj.file, as_attachment=True, filename=file_obj.name)

class FileDeleteView(BucketMixin, View):
    def post(self, request, file_id):
        file_obj = get_object_or_404(FileObject, id=file_id, bucket__organization=self.org)
        bucket = file_obj.bucket
        bucket_name = bucket.name
        filename = file_obj.name
        file_size_mb = file_obj.size / (1024 * 1024)
        
        # Delete object (triggers file deletion due to our custom delete method in models)
        file_obj.delete()
        
        # Update usage
        usage_record, _ = Usage.objects.get_or_create(user=self.org.owner)
        usage_record.storage_mb = max(0, usage_record.storage_mb - file_size_mb)
        usage_record.save()
        
        log_event(self.org, "file_deleted", bucket=bucket_name, filename=filename)
        
        # Real-time Broadcast
        broadcast(self.org, {
            'type': 'file_deleted',
            'org_name': self.org.name,
            'name': filename,
            'bucket': bucket_name,
            'storage_update': {
                'bucket_id': bucket.id,
                'usage_mb': bucket.usage_mb,
                'percent': bucket.usage_percent,
                'quota_mb': bucket.quota_mb,
                'total_org_usage_mb': usage_record.storage_mb
            }
        })
        

class APIKeyCreateView(BucketMixin, View):
    def post(self, request, bucket_name):
        bucket = get_object_or_404(Bucket, name=bucket_name, organization=self.org)
        name = request.POST.get('name', 'New Service Key')
        key = StorageKey.objects.create(bucket=bucket, name=name)
        messages.success(request, f"Generated new API Key: {key.api_key}")
        return redirect('buckets:list')

# --- Real-Time API Layer ---


class StorageAPIAuthenticationMixin:
    """Authenticates requests via StorageKey."""
    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return JsonResponse({'error': 'Authentication required. Provide X-API-KEY header.'}, status=401)
        
        try:
            self.storage_key = StorageKey.objects.get(api_key=api_key)
            self.bucket = self.storage_key.bucket
            self.org = self.bucket.organization
            # Track usage
            self.storage_key.last_used = now()
            self.storage_key.save(update_fields=['last_used'])
        except StorageKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid API Key.'}, status=401)
            
        return super().dispatch(request, *args, **kwargs)

class APIBucketDetailView(StorageAPIAuthenticationMixin, View):
    def get(self, request):
        return JsonResponse({
            'bucket': self.bucket.name,
            'object_count': self.bucket.files.count(),
            'is_public': self.bucket.is_public,
            'created_at': self.bucket.created_at.isoformat(),
            'objects': list(self.bucket.files.values('id', 'name', 'size', 'status', 'checksum'))
        })

class APIFileUploadView(StorageAPIAuthenticationMixin, View):
    def post(self, request):
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)

        # 1. Global Check
        usage_record, _ = Usage.objects.get_or_create(user=self.org.owner)
        global_limit_mb = get_org_storage_limit(self.org)
        total_new_mb = sum(f.size for f in files) / (1024 * 1024)
        
        if (usage_record.storage_mb + total_new_mb) > global_limit_mb:
            return JsonResponse({'error': 'Global Quota exceeded.'}, status=403)
            
        # 2. Bucket Check
        if (self.bucket.usage_mb + total_new_mb) > self.bucket.quota_mb:
            return JsonResponse({'error': 'Bucket Allocation full.'}, status=403)

        results = []
        for f in files:
            obj = FileObject.objects.create(
                bucket=self.bucket,
                file=f,
                name=f.name,
                size=f.size,
                content_type=f.content_type or mimetypes.guess_type(f.name)[0],
                status='processing'
            )
            start_processing_pipeline(obj.id)
            usage_record.storage_mb += (f.size / (1024 * 1024))
            usage_record.save()
            
            # Real-time Broadcast
            broadcast(self.org, {
                'type': 'file_uploaded',
                'org_name': self.org.name,
                'name': obj.name,
                'size': f.size,
                'bucket': self.bucket.name
            })
            
            results.append({'id': obj.id, 'name': obj.name, 'status': 'processing'})
            
        return JsonResponse({'status': 'uploaded', 'objects': results})

class BucketDeployView(BucketMixin, View):
    def post(self, request, bucket_name):
        bucket = get_object_or_404(Bucket, name=bucket_name, organization=self.org)
        bucket.is_live = not bucket.is_live
        if bucket.is_live:
            bucket.last_deployed_at = now()
        bucket.save()
        
        event_type = "bucket_deployed" if bucket.is_live else "bucket_deactivated"
        log_event(self.org, event_type, name=bucket.name)
        
        # Real-time Sync for Dashboard
        broadcast(self.org, {
            'type': event_type,
            'org_name': self.org.name,
            'name': bucket.name,
            'url': bucket.get_deployment_url(request)
        })
        
        return redirect('buckets:list')

class PublicServeView(View):
    def get(self, request, dist_id, filename=""):
        bucket = get_object_or_404(Bucket, distribution_id=dist_id, is_live=True)
        
        # Static Site detection (index.html fallback)
        if not filename or filename.endswith('/'):
            filename = (filename + "index.html").lstrip('/')
            
        try:
            file_obj = FileObject.objects.get(bucket=bucket, name=filename)
            content_type, _ = mimetypes.guess_type(file_obj.file.path)
            with open(file_obj.file.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type or 'application/octet-stream')
                # Professional CDN Headers
                response['X-Cache'] = 'HIT from Wire-Edge-04'
                response['X-Edge-Location'] = 'US-EAST-VA-04'
                response['Server'] = 'Wire-Edge/1.0.4'
                response['Cache-Control'] = 'public, max-age=3600'
                return response
        except FileObject.DoesNotExist:
            if filename == "index.html":
                from django.shortcuts import render
                return render(request, 'buckets/deployment_fallback.html', {
                    'bucket': bucket,
                    'now': now()
                })
            raise Http404("Distribution asset not found on edge")
        except Exception:
            raise Http404("Deployment asset not found on edge node cluster")

# --- Compute / PaaS Views ---

class AppListView(BucketMixin, ListView):
    model = App
    template_name = 'apps/list.html'
    context_object_name = 'apps'

    def get_queryset(self):
        return App.objects.filter(organization=self.org)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Statistics for the Apps dashboard
        context['total_apps'] = self.org.apps.count()
        context['live_apps'] = self.org.apps.filter(is_live=True).count()
        return context

class AppCreateView(BucketMixin, View):
    def post(self, request):
        name = request.POST.get('name')
        runtime = request.POST.get('runtime', 'django')
        
        if not name:
            messages.error(request, "Application name is required.")
            return redirect('buckets:list') # Temporary fallback

        app, created = App.objects.get_or_create(
            name=name,
            organization=self.org,
            defaults={'runtime': runtime}
        )
        
        if created:
            log_event(self.org, "app_provisioned", name=name, runtime=runtime)
            broadcast(self.org, {
                'type': 'app_created',
                'id': app.id,
                'name': name,
                'runtime': app.runtime
            })
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'app_id': app.id, 'redirect': f'/compute/a/{app.id}/'})
            messages.success(request, f"Compute App '{name}' provisioned successfully.")
        
        return redirect('buckets:app_detail', app_id=app.id)

class AppSourceUploadView(BucketMixin, View):
    def post(self, request, app_id):
        app = get_object_or_404(App, id=app_id, organization=self.org)
        artifact = request.FILES.get('file')
        
        if not artifact:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
            
        # Unified Storage Limit Check
        usage_mb = self.org.get_total_usage_mb()
        plan_limit = get_org_storage_limit(self.org)
        
        if usage_mb + (artifact.size / (1024*1024)) > plan_limit:
            return JsonResponse({'error': 'Subscription storage limit exceeded'}, status=403)
            
        # Store as a new deployment artifact
        deployment = AppDeployment.objects.create(
            app=app,
            artifact=artifact,
            status='provisioned'
        )
        
        app.source_type = 'upload'
        app.save()
        
        broadcast(self.org, {
            'type': 'app_source_updated',
            'app_id': app.id,
            'source': 'artifact_upload',
            'deployment_id': deployment.deployment_id
        })

        # Broadcast global usage update
        new_usage = self.org.get_total_usage_mb()
        broadcast(self.org, {
            'type': 'usage_update',
            'total_used_mb': new_usage,
            'plan_limit_mb': get_org_storage_limit(self.org)
        })
        
        return JsonResponse({
            'status': 'success',
            'deployment_id': deployment.deployment_id,
            'message': 'Project artifact ingested successfully'
        })

class AppDetailView(BucketMixin, DetailView):
    model = App
    template_name = 'apps/detail.html'
    context_object_name = 'app'
    pk_url_kwarg = 'app_id'

    def get_queryset(self):
        return App.objects.filter(organization=self.org)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deployments'] = self.object.deployments.all()[:10]
        context['env_vars'] = self.object.env_vars.all()
        # Infrastructure Governance
        context['total_used_mb'] = self.org.get_total_usage_mb()
        context['plan_limit_mb'] = get_org_storage_limit(self.org)
        context['remaining_mb'] = max(0, context['plan_limit_mb'] - context['total_used_mb'])
        return context

class AppDeployView(BucketMixin, View):
    def post(self, request, app_id):
        app = get_object_or_404(App, id=app_id, organization=self.org)
        
        # Source Validation
        last_deployment = app.deployments.first()
        if not last_deployment or not last_deployment.artifact:
            if not app.source_url:
                return JsonResponse({'error': 'No project source (Upload or Git) detected. Please provide a source before deploying.'}, status=400)

        # Create a new deployment record if we are deploying from a Git URL
        # or reuse the one that was just uploaded.
        if app.source_type == 'github':
            deployment = AppDeployment.objects.create(app=app, status='building')
        else:
            deployment = last_deployment
            deployment.status = 'building'
            deployment.save()

        app.status = 'building'
        app.save()

        # Trigger the Orchestrator Pipeline
        start_app_deployment_pipeline(deployment.id)
        
        return JsonResponse({
            'status': 'building',
            'deployment_id': deployment.deployment_id
        })

class AppUpdateConfigView(BucketMixin, View):
    def post(self, request, app_id):
        app = get_object_or_404(App, id=app_id, organization=self.org)
        path = request.POST.get('provisioning_path')
        
        if path:
            # Basic validation: Check if path is writeable or valid format
            # In a real industrial app, we'd do deeper OS-level validation
            app.provisioning_path = path
            app.save()
            
            log_event(self.org, "app_config_updated", name=app.name, path=path)
            
            return JsonResponse({'status': 'success', 'path': path})
        
        return JsonResponse({'error': 'No path provided'}, status=400)

class OrgUpdateConfigView(BucketMixin, View):
    def post(self, request):
        path = request.POST.get('deployment_root')
        if path:
            self.org.deployment_root = path
            self.org.save()
            log_event(self.org, "org_hub_updated", path=path)
            return JsonResponse({'status': 'success', 'path': path})
        return JsonResponse({'error': 'No path provided'}, status=400)
