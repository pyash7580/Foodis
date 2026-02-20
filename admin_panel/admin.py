from django.contrib import admin
from .models import Banner, Commission, SitePolicy, SystemSettings


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'rate', 'effective_from', 'effective_until']
    list_filter = ['effective_from', 'effective_until']
    search_fields = ['restaurant__name']


@admin.register(SitePolicy)
class SitePolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'policy_type', 'slug', 'is_active', 'updated_at']
    list_filter = ['policy_type', 'is_active']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
    search_fields = ['key', 'description']

