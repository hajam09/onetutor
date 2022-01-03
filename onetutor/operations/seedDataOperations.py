import xml.etree.ElementTree as ET
from pathlib import Path

from django.apps import apps


def runSeedDataInstaller():
    xmlFiles = getSeedDataFiles()

    for xmlFile in xmlFiles:
        installSeedData(xmlFile)


def installSeedData(xmlFile):
    tree = ET.parse(xmlFile)

    if tree.getroot().tag != "SeedData":
        return

    for element in tree.getroot():
        tableName = element.tag
        appName = getAppLabelForModel(tableName)
        modelType = apps.get_model(appName, tableName)

        newKeys = {}
        oldKeys = []

        # change "." -> "__" to search for foreign key objects.
        for key, value in element.attrib.items():
            if "." in key:
                newKey = key.replace(".", "__")
                newKeys[newKey] = value
                oldKeys.append(key)

        # delete keys which have "." in them
        for key in oldKeys:
            del element.attrib[key]

        # add new keys which replaced "." with "__"
        element.attrib = element.attrib | newKeys

        if modelType.objects.filter(**element.attrib):
            continue

        modelInstance = modelType()
        for key, value in element.attrib.items():
            setattr(modelInstance, getKeyOrForeignObjectId(key), getValueOrForeignObjectId(key, value))
        modelInstance.save()


def getKeyOrForeignObjectId(key):
    """
    if a foreign object is being looked up such as componentGroup__internalKey
    then change the "internalKey" to "id".
    the getValueOrForeignObjectId() will return the id for object componentGroup where internalKey="value"
    """
    if "__" not in key:
        return key

    keySplit = key.split("__")
    keySplit[-1] = "id"

    return "_".join(keySplit)


def getValueOrForeignObjectId(key, value):
    """
    if a foreign object is being looked up such as componentGroup__internalKey
    then return the id of the object being looked up
    the modelInstance stores the id of the foreign object and not the actual object itself
    """
    if "__" not in key:
        return value

    tableName = key.split("__")[0]
    appName = getAppLabelForModel(tableName)

    modelType = apps.get_model(appName, tableName)
    return modelType.objects.get(**{key.split("__")[1]: value}).id


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


def getSeedDataFiles():
    return [str(p) for p in Path("seed-data").rglob('*.xml')]
