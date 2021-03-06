/*
 Copyright (C) 2017 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import '../object-list-item/comment-list-item';
import '../object-list/object-list';

(function (can, GGRC) {
  'use strict';

  var tpl = can.view(GGRC.mustache_path +
    '/components/comment/mapped-comments.mustache');
  var tag = 'mapped-comments';
  /**
   * Assessment specific mapped controls view component
   */
  can.Component.extend({
    tag: tag,
    template: tpl,
    viewModel: {
      define: {
        noItemsText: {
          type: 'string',
          value: '',
        },
      },
      mappedItems: [],
    },
  });
})(window.can, window.GGRC);
