import secrets
import hashlib
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from saas.models import Organization

class Bucket(models.Model):
    name = models.SlugField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='buckets')
    is_public = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    distribution_id = models.CharField(max_length=20, unique=True, blank=True)
    edge_status = models.CharField(max_length=20, default='ready') # ready, provisioning, deactivated
    quota_mb = models.IntegerField(default=1024) # Manual allocation in MB
    created_at = models.DateTimeField(auto_now_add=True)
    last_deployed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'organization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name}/{self.name}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"bucket-{self.organization.id}"
        self.name = slugify(self.name)
        
        if not self.distribution_id:
            import uuid
            self.distribution_id = f"dist-{uuid.uuid4().hex[:8]}"
            
        super().save(*args, **kwargs)

    def get_deployment_url(self, request=None):
        if not self.is_live:
            return None
        # AWS style technical URL
        path = f"/storage/s/{self.distribution_id}/"
        if request:
            return request.build_absolute_uri(path)
        return path

    @property
    def usage_mb(self):
        # Calculate from FileObjects
        total_bytes = self.files.aggregate(models.Sum('size'))['size__sum'] or 0
        return total_bytes / (1024 * 1024)
    
    @property
    def usage_gb(self):
        return self.usage_mb / 1024

    @property
    def quota_gb(self):
        return self.quota_mb / 1024
    
    @property
    def usage_percent(self):
        if self.quota_mb <= 0: 
            return 0
        return min(round((self.usage_mb / self.quota_mb) * 100, 1), 100)
    
    @property
    def progress_dash_offset(self):
        # Circumference is 552.92
        circumference = 552.92
        percent = self.usage_percent
        offset = circumference - (percent / 100) * circumference
        return offset

class StorageKey(models.Model):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=50, default='Default Key')
    api_key = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = f"wire_7374_{secrets.token_urlsafe(32)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.bucket.name})"

def bucket_upload_path(instance, filename):
    # uploads to media/buckets/org_id/bucket_name/filename
    return f"buckets/{instance.bucket.organization.id}/{instance.bucket.name}/{filename}"

class FileObject(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]

    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=bucket_upload_path)
    name = models.CharField(max_length=255)
    size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=100, blank=True)
    checksum = models.CharField(max_length=64, blank=True) # SHA-256
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.bucket.name}/{self.name}"

    def calculate_checksum(self):
        sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            sha256.update(chunk)
        return sha256.hexdigest()

    def save(self, *args, **kwargs):
        if not self.pk and self.file:
            # New file - initial processing
            if not self.size:
                self.size = self.file.size
            if not self.checksum:
                # Note: We do this on save, but for very large files we should do it in background
                # For this 'useful' simulation, we do a small chunk or handle it carefully
                pass 
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)

class SharedLink(models.Model):
    file_object = models.ForeignKey(FileObject, on_delete=models.CASCADE, related_name='shared_links')
    token = models.CharField(max_length=100, unique=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Link for {self.file_object.name}"


class App(models.Model):
    STATUS_CHOICES = [
        ('ready', 'Provisioned'),
        ('building', 'Building'),
        ('live', 'Live'),
        ('error', 'Build Failed'),
        ('deactivated', 'Offline'),
    ]
    
    name = models.SlugField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='apps')
    runtime = models.CharField(max_length=50, default='django') # Now dynamic (django, node, go, rust, etc.)
    distribution_id = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    
    # Ingestion Metadata
    source_type = models.CharField(max_length=20, choices=[('upload', 'Artifact Upload'), ('github', 'GitHub Repo')], default='upload')
    source_url = models.URLField(blank=True, null=True) # Repo URL or similar
    
    is_live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_deployed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'organization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.runtime})"

    def save(self, *args, **kwargs):
        if not self.distribution_id:
            import uuid
            self.distribution_id = f"app-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def get_deployment_url(self, request=None):
        if not self.is_live:
            return None
        path = f"/compute/a/{self.distribution_id}/"
        if request:
            return request.build_absolute_uri(path)
        return path

class EnvironmentVariable(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='env_vars')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255) # In production we would encrypt this
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('app', 'key')

    def __str__(self):
        return f"{self.key} for {self.app.name}"

class AppDeployment(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='deployments')
    deployment_id = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, default='queued')
    logs = models.TextField(blank=True, default='')
    
    # Store the actual project artifact if uploaded
    artifact = models.FileField(upload_to='deployments/artifacts/%Y/%m/%d/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.deployment_id:
            import uuid
            self.deployment_id = f"dep-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Deployment {self.deployment_id} for {self.app.name}"
