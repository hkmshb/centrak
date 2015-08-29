(function($) {
    var DataTable = function($element, options) {
        this.$element = $element;
        this.options  = ($o = $.extend({}, DataTable.DEFAULTS, options));
        this.$pagination = $element.find($o.pagination);
        this.triggers = {
            $toggler: $element.find($o.toggle),
            $deleter: $element.find($o.delete),
        };
        
        _DoBindings(this);
    };
    
    DataTable.DEFAULTS = {
        target: '[data-bind="table"]',
        toggle: '[data-toggle="checked"]',
        delete: '[name="btn_delete"]',
        pagination: '.pagination-packed',
    };
    
    DataTable.prototype.toggle = function(trigger) {
        var $trigger = $(trigger)
          , $datarows = $trigger.data('hs.datarows');
        
        if (!$datarows) {
            var target = $trigger.attr('data-target') || $trigger.attr('href')
              , selector = '[name="' + target + '"]';
            
            $datarows = this.$element.find(selector);
            $trigger.data('hs.datarows', $datarows);
        };
        
        $datarows.each(function() {
            this.checked = trigger.checked;
        });
    };
    
    DataTable.prototype.delete = function() {
        var $selection = this.$element.find('tbody input:checked')
          , msg_sel_items = "Record(s) to be deleted must be selected first."
          , msg_del_single = "Do you really want to delete this record?"
          , msg_del_multiple = "Do you really want to delete the selected {} record(s)?";
        
        if (!$selection || $selection.length == 0) {
            alert(msg_sel_items);
        } else {
            var msg = $selection.length == 1
                    ? msg_del_single
                    : msg_del_multiple.replace(/{}/g, $selection.length);
            if (confirm(msg)) {
                this.$element.submit();
            };
        }
    };
    
    DataTable.prototype.bindPaginator = function() {
        var that = this
          , pagingNumbers = this.options.pagingNumbers
          , indexTable = { first:0, prev:1, next:2, last:3 };
        
        this.$pagination.find('.controls span').on('click', function() {
            var $this = $(this)
              , index = indexTable[$this.attr('name')];            
            window.location = _buildQueryString('page=' + pagingNumbers[index]);
        });
        
        this.$pagination.find('.summary select').on('change', function() {
            var $this = $(this);
            _changePageSize($this.val());
        });
    };
    
    function _changePageSize(size) {
        var pathname = window.location.pathname;
        window.location = pathname + '?pageSize=' + size;
    };
    
    function _buildQueryString(page) {
        var url = window.location.pathname
          , qs  = window.location.search
          , q   = page;
        
        if (qs && qs.length > 0) {
            $(qs.substr(1).split('&')).each(function() {
                if (!this.startsWith('page='))
                    q += "&" + this;
            });
        }
        return url + '?' + q;
    };
    
    function _DoBindings(table) {
        var triggers = table.triggers;
        
        // bind to selection toggle        
        triggers.$toggler.on('click', function() {
            table.toggle.call(table, this);;
        });
        
        // bind to delete action
        triggers.$deleter.on('click', function() {
            table.delete.call(table, this);
        });
        
        // paginator bindings
        table.bindPaginator();
    };
    
    $('[data-bind="table"]').each(function() {
        var $this   = $(this)
          , options = $.extend({}, $this.data());
        
        $this.data('hs.data-table', new DataTable($this, options));
    });
})(jQuery);
