from .base import *
from ggrc.models import Directive, Control
from .base_row import *
from collections import OrderedDict
from ggrc.models.control import CATEGORY_CONTROL_TYPE_ID, CATEGORY_ASSERTION_TYPE_ID

class ControlRowConverter(BaseRowConverter):
  model_class = Control

  def setup_object(self):
    self.obj = self.setup_object_by_slug(self.attrs)
    if self.obj.directive \
       and self.obj.directive is not self.importer.options.get('directive'):
          self.importer.errors.append('Slug code is already used.')
    else:
      self.obj.directive = self.importer.options.get('directive')

  def reify(self):
    self.handle('slug', SlugColumnHandler)
    self.handle_date('start_date')
    self.handle_date('stop_date')
    self.handle_date('created_at', no_import = True)
    self.handle_date('updated_at', no_import = True)
    self.handle_text_or_html('description')
    self.handle_text_or_html('documentation_description')

    self.handle_raw_attr('title')
    self.handle_raw_attr('url')

    self.handle_option('kind', role = 'control_kind')
    self.handle_option('means', role = 'control_means')
    self.handle_option('verify_frequency')

    self.handle_boolean('key_control', truthy_values = ['key', 'key_control', 'key control'])
    self.handle_boolean('fraud_related', truthy_values = ['fraud', 'fraud_related', 'fraud related'])
    self.handle_boolean('active', truthy_values = ['active'])

    self.handle('documents', LinkDocumentsHandler)
    self.handle('categories', LinkCategoriesHandler, scope_id = CATEGORY_CONTROL_TYPE_ID)
    self.handle('assertions', LinkCategoriesHandler, scope_id = CATEGORY_ASSERTION_TYPE_ID)
    self.handle('people_responsible', LinkPeopleHandler, role = 'responsible')
    self.handle('people_accountable', LinkPeopleHandler, role = 'accountable')
    self.handle('systems', LinkSystemsHandler, is_biz_process = False)
    self.handle('processes', LinkSystemsHandler, association = 'systems', is_biz_process = True)

  def save_object(self, db_session, **options):
    if options.get('directive_id'):
      self.obj.directive_id = int(options.get('directive_id'))
      db_session.add(self.obj)

class ControlsConverter(BaseConverter):

  metadata_map = OrderedDict([
    ('Type', 'type'),
    ('Directive Code', 'slug')
  ])

  object_map = OrderedDict([
    ('Control Code', 'slug'),
    ('Title', 'title'),
    ('Description', 'description'),
    ('Kind', 'kind'),
    ('Means', 'means'),
    ('Version', 'version'),
    ('Start Date', 'start_date'),
    ('Stop Date', 'stop_date'),
    ('URL', 'url'),
    ('Link:Systems', 'systems'),
    ('Link:Processes', 'processes'),
    ('Link:Categories', 'categories'),
    ('Link:Assertions', 'assertions'),
    ('Documentation', 'documentation_description'),
    ('Frequency', 'verify_frequency'),
    ('References', 'documents'),
    ('Link:People;Responsible','people_responsible'),
    ('Link:People;Accountable', 'people_accountable'),
    ('Key Control', 'key_control'),
    ('Active', 'active'),
    ('Fraud Related', 'fraud_related'),
    ('Created', 'created_at'),
    ('Updated' ,'updated_at')
  ])

  row_converter = ControlRowConverter

  def validate_metadata(self, attrs):
    self.validate_metadata_type(attrs, "Controls")
    self.validate_code(attrs)

  def directive(self):
    return self.options['directive']

  def do_export_metadata(self):
    yield self.metadata_map.keys()
    yield ['Controls', self.directive().slug]
    yield[]
    yield[]
    yield self.object_map.keys()

