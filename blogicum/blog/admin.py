from django.contrib import admin
from .models import Post, Category, Location


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'pub_date',
        'category',
        'location',
        'is_published',
    )
    list_filter = (
        'is_published',
        'pub_date',
        'category',
        'location',
        'author',
    )
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'text',
                    'author',
                    'category',
                    'location',
                    'is_published',
                )
            },
        ),
        (
            'Дополнительно',
            {
                'fields': ('pub_date', 'created_at'),
                'classes': ('collapse',),
            },
        ),
    )
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    ordering = ('title',)
    readonly_fields = ('created_at',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at',)
