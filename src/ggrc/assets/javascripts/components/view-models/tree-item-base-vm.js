/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import * as TreeViewUtils from '../../plugins/utils/tree-view-utils';
import {
  getPageType,
} from '../../plugins/utils/current-page-utils';
import {
  getWidgetConfig,
} from '../../plugins/utils/object-versions-utils';

export default can.Map.extend({
  define: {
    expanded: {
      type: Boolean,
      value: false,
    },
  },
  instance: null,
  /**
   * Result from mapping
   */
  result: null,
  resultDfd: null,
  limitDepthTree: 0,
  itemSelector: '',
  childModelsList: [],
  /**
   * List of models for show in sub-level for current item.
   */
  selectedChildModels: [],
  $el: null,
  initChildTreeDisplay: function () {
    var modelName = this.attr('instance').type;
    var models = TreeViewUtils.getModelsForSubTier(modelName);

    var displayList = models.available.map(function (model) {
      return {
        widgetName: getWidgetConfig(model).widgetName,
        name: model,
        display: models.selected.indexOf(model) !== -1,
      };
    });

    this.attr('childModelsList', displayList);
    this.attr('selectedChildModels', models.selected);
  },
  setChildModels: function (selected) {
    this.attr('selectedChildModels', selected);
  },
  onExpand: function (event) {
    var isExpanded = this.attr('expanded');

    if (event && isExpanded !== event.state) {
      if (isExpanded !== event.state) {
        this.attr('expanded', event.state);
      }
    } else {
      this.attr('expanded', !isExpanded);
    }
  },
  onClick: function ($element) {
    var instance = this.attr('instance');

    switch (instance.attr('type')) {
      case 'Person':
        if (!this.attr('result')) {
          this.attr('resultDfd').then(()=> {
            this.select($element);
          });
          return;
        }
        break;
      case 'Cycle':
      case 'CycleTaskGroup':
        if (getPageType() === 'Workflow') {
          this.attr('expanded', !this.attr('expanded'));
          return;
        }
        break;
    }

    this.select($element);
  },
  collapseAndHighlightItem: function () {
    const animationDuration = 2000;
    let el = this.attr('$el');
    this.attr('expanded', false);

    el.addClass('tree-item-refresh-animation')
      .delay(animationDuration)
      .queue((next) => {
        el.removeClass('tree-item-refresh-animation');
        next();
      });
  },
  select: function ($element) {
    var instance = this.attr('instance');
    var itemSelector = this.attr('itemSelector');

    $element = $element.closest(itemSelector);

    can.trigger($element, 'selectTreeItem', [$element, instance]);
  },
});
