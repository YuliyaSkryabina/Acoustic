"""QGIS плагин Акустик — точка входа."""


def classFactory(iface):
    from .acoustik_plugin import AcoustikPlugin
    return AcoustikPlugin(iface)
