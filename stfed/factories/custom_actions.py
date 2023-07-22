# def __get_custom_actions_for_resource(self, rt: stfed.model.ResourceType, resource: str):
#     def make_action(name, handler):
#         action = QAction(name, self)
#         action.triggered.connect(handler)
#         return action
#     if rt == stfed.model.ResourceType.PAL:
#         return [
#             # make_action("Export as PCX", self.__export_pal_as_pcx),
#             # make_action("Export as HTML"),
#         ]
#     return []