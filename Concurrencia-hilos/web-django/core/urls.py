from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('hilos/', views.probar_hilos, name='probar_hilos'),
    path("probar-algoritmo/", views.probar_algoritmo, name="probar_algoritmo"),
    path("historial/", views.historial_corridas, name="historial_corridas"),
    path("historial-html/", views.pagina_historial, name="pagina_historial"),
    path("historial-json/", views.historial_corridas, name="historial_json"),
    path("convergencias-json/", views.convergencias_json, name="convergencias_json"),
    path("exportar-excel/", views.exportar_excel, name="exportar_excel"),
    path("eliminar-corridas/",views.eliminar_corridas, name="eliminar_corridas"),
    path("comparar/", views.comparar_rendimiento, name="comparar_rendimiento"),
    path("comparaciones-json/", views.comparaciones_json, name="comparaciones_json"),
    path("limpiar-comparaciones/", views.limpiar_comparaciones, name="limpiar_comparaciones"),
]
