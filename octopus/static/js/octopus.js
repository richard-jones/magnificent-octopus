var octopus = {
    display : {
        hidden : {},

        hideOffScreen : function(selector) {
            var el = $(selector);
            if (selector in this.hidden) { return }
            this.hidden[selector] = {"position" : el.css("position"), "margin" : el.css("margin-left")};
            $(selector).css("position", "absolute").css("margin-left", -9999);
        },

        bringIn : function(selector) {
            var pos = this.hidden[selector].position;
            var mar = this.hidden[selector].margin;
            $(selector).css("position", pos).css("margin-left", mar);
            delete this.hidden[selector];
        }
    }
};
