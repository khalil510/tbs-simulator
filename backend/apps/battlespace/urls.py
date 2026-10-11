from rest_framework.routers import DefaultRouter

from .views import BattlespaceViewSet, ObjectiveViewSet, ScenarioEntityViewSet, ScenarioViewSet

router = DefaultRouter()
router.register("battlespaces", BattlespaceViewSet, basename="battlespace")
router.register("scenarios", ScenarioViewSet, basename="scenario")
router.register("scenario-entities", ScenarioEntityViewSet, basename="scenario-entity")
router.register("objectives", ObjectiveViewSet, basename="objective")

urlpatterns = router.urls
