from django.urls import path, include, re_path
from dashboard import views

app_name = "dashboard"

urlpatterns = [
	# Render all the templates
	path('<slug:template>/', views.index, name='template'),
]