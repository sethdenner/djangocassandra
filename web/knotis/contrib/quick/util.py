import django.db.models as models

quick_models = {}

def register_quick_models(module):
    for model in module.__models__:
        register_quick_model(getattr(module,model))

def register_quick_model(model):
    quick_models[model.__name__.lower()]=model

def get_quick_models():
    return quick_models.values()

def get_quick_model_names():
    return quick_models.keys()

def get_quick_view(request, model, *args, **kwargs):
    quick_model = quick_models.get(model)
    if (not issubclass(quick_model, models.Model)):
        raise quick.errors.ExceptionModelInvalid()
    return quick_model.Quick.view.as_view()(request, model=quick_model, *args, **kwargs)
