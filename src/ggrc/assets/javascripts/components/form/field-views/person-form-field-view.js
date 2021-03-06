/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import '../../object-list-item/person-list-item';

(function (can, GGRC) {
  'use strict';

  GGRC.Components('personFormFieldView', {
    tag: 'person-form-field-view',
    template: can.view(
      GGRC.mustache_path + '/components/form/' +
        'field-views/person-form-field-view.mustache'
    ),
    viewModel: {
      value: null,
      disabled: false
    }
  });
})(window.can, window.GGRC);
