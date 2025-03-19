from django.urls import path
from . import views

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('upload/', views.image_upload, name='image_upload'),
    path('<uuid:image_id>/', views.image_detail, name='image_detail'),
    path('<uuid:image_id>/download/', views.image_download, name='image_download'),
    path('<uuid:image_id>/view/', views.image_view, name='image_view'),
    path('<uuid:image_id>/thumbnail/', views.thumbnail_view, name='thumbnail_view'),
    path('<uuid:image_id>/delete/', views.image_delete, name='image_delete'),
]
