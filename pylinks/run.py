from links import app
from links.link import resources as link_resources

modules = [link_resources, ]

for module in modules:
    module.register(app, url_prefix='/api/v1')
app.run(debug=True)
