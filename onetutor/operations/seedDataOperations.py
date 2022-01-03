import xml.etree.ElementTree as ET
from pathlib import Path

from django.apps import apps


def installSeedData():
    xmlLocations = getXMLFileLocations()

    for xmlFiles in xmlLocations:
        tree = ET.parse(xmlFiles)

        if tree.getroot().tag != "SeedData":
            continue

        for element in tree.getroot():
            tableName = element.tag
            appName = getAppLabelForModel(tableName)

            modelType = apps.get_model(appName, tableName)
            if modelType.objects.filter(**element.attrib):
                continue

            modelInstance = modelType()
            for key, value in element.attrib.items():
                setattr(modelInstance, key, value)
            modelInstance.save()
    return


def getAppLabelForModel(modalName):
    appLabel = [
        app.label
        for app in apps.get_app_configs()
        for model in app.models
        if modalName.lower() in model
    ]

    appLabel = set(appLabel)

    if len(appLabel) > 1:
        raise RuntimeWarning("Expected single app to be found for this model " + modalName)

    if len(appLabel) == 0:
        raise RuntimeWarning("No app to be found for this model " + modalName)

    return list(appLabel)[0]


def getXMLFileLocations():
    return [str(p) for p in Path("seed-data").rglob('*.xml')]
