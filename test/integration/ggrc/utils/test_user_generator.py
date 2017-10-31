# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for user generator"""

from collections import OrderedDict

import json
import mock

from ggrc.converters import errors
from ggrc.integrations.client import PersonClient
from ggrc.models import Assessment
from ggrc.models import AssessmentTemplate
from ggrc.models import Audit
from ggrc.models import Person
from ggrc_basic_permissions.models import Role
from ggrc_basic_permissions.models import UserRole

from integration.ggrc.services import TestCase
from integration.ggrc.models import factories


class TestUserGenerator(TestCase):
  """Test user generation."""

  def setUp(self):
    super(TestUserGenerator, self).setUp()
    self.clear_data()
    self.client.get("/login")

  def _post(self, data):
    return self.client.post(
        '/api/people',
        content_type='application/json',
        data=data,
        headers=[('X-Requested-By', 'Unit Tests')],
    )

  @staticmethod
  def _mock_post(*args, **kwargs):
    """Mock of IntegrationService _post"""
    # pylint: disable=unused-argument
    payload = kwargs["payload"]
    res = []
    for name in payload["usernames"]:
      res.append({'firstName': name,
                  'lastName': name,
                  'username': name})
    return {'persons': res}

  @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
  @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
  def test_user_generation(self):
    """Test user generation."""
    with mock.patch.multiple(
        PersonClient,
        _post=self._mock_post
    ):
      data = json.dumps([{'person': {
          'name': 'Alan Turing',
          'email': 'aturing@example.com',
          'context': None,
          'external': True
      }}])
      response = self._post(data)
      self.assertStatus(response, 200)

      user = Person.query.filter_by(email='aturing@example.com').one()
      self.assertEqual(user.name, 'Alan Turing')

      roles = UserRole.query.filter_by(person_id=user.id)
      self.assertEqual(roles.count(), 1)

  @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
  @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
  def test_user_creation(self):
    """Test user creation."""
    with mock.patch.multiple(
        PersonClient,
        _post=self._mock_post
    ):
      data = json.dumps([{'person': {
          'name': 'Alan Turing',
          'email': 'aturing@example.com',
          'context': None
      }}])
      response = self._post(data)
      self.assertStatus(response, 200)

      user = Person.query.filter_by(email='aturing@example.com').one()
      self.assertEqual(user.name, 'Alan Turing')

      roles = UserRole.query.filter_by(person_id=user.id)
      self.assertEqual(roles.count(), 0)

  @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
  @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
  def test_wrong_user_creation(self):
    """Test wrong user creation."""
    with mock.patch.multiple(
        PersonClient,
        _post=mock.MagicMock(return_value={'persons': []})
    ):
      data = json.dumps([{'person': {
          'name': 'Alan Turing',
          'email': 'aturing@example.com',
          'context': None,
          'external': True
      }}])
      response = self._post(data)
      self.assertStatus(response, 406)

      user = Person.query.filter_by(email='aturing@example.com').first()
      self.assertIsNone(user)

  @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
  @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
  def test_person_import(self):
    """Test for mapped person"""
    with mock.patch.multiple(
        PersonClient,
        _post=self._mock_post
    ):
      program = factories.ProgramFactory()
      audit_slug = 'Audit1'
      self.import_data(OrderedDict([
          ("object_type", "Audit"),
          ("Code*", audit_slug),
          ("Program*", program.slug),
          ("Auditors", "cbabbage@example.com"),
          ("Title", "Title"),
          ("Status", "Planned"),
          ("Audit Captain", "aturing@example.com")
      ]))
      audit = Audit.query.filter(Audit.slug == audit_slug).first()
      self.assertEqual("aturing@example.com", audit.contact.email)
      auditor = Person.query.filter(
          Person.email == "cbabbage@example.com").first()
      role = Role.query.filter(Role.name == "Auditor").first()
      user_role = UserRole.query.filter_by(person_id=auditor.id,
                                           role_id=role.id).first()
      self.assertIsNotNone(user_role)

      assessment_slug = "Assessment1"
      self.import_data(OrderedDict([
          ("object_type", "Assessment"),
          ("Code*", assessment_slug),
          ("Audit*", audit.slug),
          ("Creators*", "aturing@example.com"),
          ("Assignees*", "aturing@example.com"),
          ("Secondary Contacts", "cbabbage@example.com"),
          ("Title", "Title")
      ]))
      assessment = Assessment.query.filter(
          Assessment.slug == assessment_slug).first()
      self.assertEqual("aturing@example.com", assessment.creators[0].email)
      self.assertEqual("cbabbage@example.com",
                       assessment.access_control_list[0].person.email)

  @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
  @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
  def test_persons_import(self):
    """Test for mapped persons"""
    with mock.patch.multiple(
        PersonClient,
        _post=self._mock_post
    ):
      audit = factories.AuditFactory()

      slug = "AssessmentTemplate1"
      response = self.import_data(OrderedDict([
          ("object_type", "Assessment_Template"),
          ("Code*", slug),
          ("Audit*", audit.slug),
          ("Default Assignee", "aturing@example.com"),
          ("Default Verifier", "aturing@example.com\ncbabbage@example.com"),
          ("Title", "Title"),
          ("Object Under Assessment", 'Control'),
      ]))
      self._check_csv_response(response, {})
      assessment_template = AssessmentTemplate.query.filter(
          AssessmentTemplate.slug == slug).first()

      self.assertEqual(len(assessment_template.default_people['verifiers']), 2)
      self.assertEqual(len(assessment_template.default_people['assessors']), 1)

  @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
  @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
  def test_wrong_person_import(self):
    """Test for wrong person import"""
    with mock.patch.multiple(
        PersonClient,
        _post=mock.MagicMock(return_value={'persons': [{
            'firstName': "Alan",
            'lastName': 'Turing',
            'username': "aturing"}]})
    ):
      audit = factories.AuditFactory()
      slug = "AssessmentTemplate1"
      response = self.import_data(OrderedDict([
          ("object_type", "Assessment_Template"),
          ("Code*", slug),
          ("Audit*", audit.slug),
          ("Default Assignee", "aturing@example.com"),
          ("Default Verifier", "aturing@example.com\ncbabbage@example.com"),
          ("Title", "Title"),
          ("Object Under Assessment", 'Control'),
      ]))
      self._check_csv_response(
          response,
          {"Assessment Template": {
              "row_warnings": {errors.UNKNOWN_USER_WARNING.format(
                  line=3, email="cbabbage@example.com")}}})