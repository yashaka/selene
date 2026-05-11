/*
# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/
$(document).ready(function(){

    // temporary solution for some specific waiting emulation
    // TODO: find a way to use setTimeout instead as in other cases
    function hardWait(milliseconds) {
        var start = new Date().getTime();
        for (var i = 0; i < 1e7; i++) {
            if ((new Date().getTime() - start) > milliseconds){
                break;
            }
        }
    }

    function imitateLoading(fn){
        setTimeout(fn, 500)
    }

    var item = '[id^="item"]';
    var itemsCounter = 0;
    var $templateItem = $('#template_item');
    var $templateOptionsFilter = $('#template_options_filter');

    $('.hidden_by_default').hide()

    function toggleCheckbox(){
        var $this = $(this);
        imitateLoading(function(){
            $this.next().toggle($this.prop('checked'));
        });
    }

    $('#order_items')
        .on('click', '#add_item', function(){
            var $newItem = $templateItem.clone()
                .attr('id','item_' + (++itemsCounter));

            hardWait(1000)  // TODO: refactor to use imitateLoading()
            $(this).before($newItem);  // TODO: delay adding this element to the dom also
            imitateLoading(function(){
                $newItem.show();
            })
        })
        .on('click', item + ' .show_advanced_options', toggleCheckbox)
        .on('click', item + ' .show_advanced_options_selector', toggleCheckbox)
        .on('click', item + ' .add_options_filter', function(){
            var itemNumber = parseInt($(this).parent().parent().attr('id').match(/^item_(.+)$/).pop());
            var newFilterNumber = $(this).parent().find('[id^="options_filter"]').size() + 1;

            var $newOptionsFilter = $templateOptionsFilter.clone()
                .attr('id', 'options_filter_' + itemNumber + '_' + newFilterNumber);

            $(this).before($newOptionsFilter);

            imitateLoading(function (){
                $newOptionsFilter.show()
            });
        })
        .on('change', item + ' [id^=options_filter] .options_scope_type', function(){
            var selectedType = $(this).val();
            $(this).parent().find('.options_scope option').each(function(){
                var currentText = $(this).text();
                $(this).text(currentText.slice(0,-1) + selectedType.slice(-1));
            });
        })
        .on('click', item + ' .apply_filtered_options', function(){
            var $item = $(this).parent().parent();
            var $optionsList = $item.find('.options_list');
            var $optionsListPlaceholder = $item.find('.options_list_placeholder');
            $optionsList.hide();
            $optionsListPlaceholder.show();
            imitateLoading(function(){
                $item.find('[id^="options_filter"]').each(function(){
                    var scope = $(this).find('.options_scope').val();
                    $optionsList.append($('<li>' + scope + '</li>'));
                });
                $optionsListPlaceholder.hide(3000, function(){
                    $optionsList.show();
                });
            });
        })
        .on('click', item + ' .clear_options', function(){
            var $item = $(this).parent().parent();
            var $optionsList = $item.find('.options_list');
            imitateLoading(function(){
                $optionsList.empty();
            });
        });
});
