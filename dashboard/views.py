from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template

@login_required
def index(request, template="index"):
	print(template)
	return render(request, "dashboard/"+template+".html")

@login_required
def pages(request):
	print("ss")
	context = {}
	# All resource paths end in .html.
	# Pick out the html file name from the url. And load that template.
	try:
		load_template = "dashboard/"+request.path.split('/')[-1]
		html_template = loader.get_template( load_template )
		return HttpResponse(html_template.render(context, request))
		
	except template.TemplateDoesNotExist:

		html_template = loader.get_template( 'dashboard/page-404.html' )
		return HttpResponse(html_template.render(context, request))

	except:
	
		html_template = loader.get_template( 'page-500.html' )
		return HttpResponse(html_template.render(context, request))