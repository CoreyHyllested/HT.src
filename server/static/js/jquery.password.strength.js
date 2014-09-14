;(function ( $, window, document, undefined ) {

    var pluginName = "PasswordStrengthManager",
    defaults = {
        password: "",
        confirm_pass : "",
        blackList : [],
        minChars : "",
        maxChars : "",
        advancedStrength : true
    };

    function Plugin ( element, options ) {
        this.element = element;
        this.settings = $.extend( {}, defaults, options );
        this._defaults = defaults;
        this._name = pluginName;
        this.init();

        this.info = '';
    }

    Plugin.prototype = {
        init: function () {

       
            var errors = this.customValidators();
            // if('' == this.settings.password || '' == this.settings.confirm_pass){

            //     this.info = 'Please choose a password';
            // }
            // else if(this.settings.password != this.settings.confirm_pass){
            if(this.settings.password != this.settings.confirm_pass){

                this.info = 'Passwords don\'t match';
                this.color = '#e75f63';
            } else if(errors == 0){
                var strength =  '';
                strength = zxcvbn(this.settings.password, this.settings.blackList);

                console.log("strength:");
                console.log(strength);
                switch(strength.score){
                    case 0:
                        this.info = 'Password Strength: Very Weak';
                        this.color = '#e75f63';
                        break;
                    case 1:
                        this.info = 'Password Strength: Weak';
                        this.color = '#e75f63';
                        break;
                    case 2:
                        this.info = 'Password Strength: Weak';
                        this.color = '#e75f63';
                        
                        break;
                    case 3:
                        this.info = 'Password Strength: Medium';
                        this.color = '#c88c1e';
                        break;
                    case 4:

                        if(this.settings.advancedStrength){
                            var crackTime = String(strength.crack_time_display);

                            if (crackTime.indexOf("years") !=-1) {
                                this.info = 'Password Strength: Very Strong';
                                this.color = '#59a6a6';
                            }else if(crackTime.indexOf("centuries") !=-1){
                                this.info = 'Password Strength: Perfect';
                                this.color = '#59a6a6';
                            }
                        }else{
                        this.info = 'Password Strength: Strong';
                        this.color = '#59a6a6';
                        }
                        break;
                }

            }


            $(this.element).html(this.info).css("color", this.color).slideDown();

        },
        minChars: function () {
            if(this.settings.password.length < this.settings.minChars){
                this.info = 'Password needs at least '+ this.settings.minChars  + ' characters';
                this.color = '#e75f63';
                return false;
            }else{
                return true;
            }
        },
        maxChars: function () {
            if(this.settings.password.length > this.settings.maxChars){
                this.info = 'Password should have maximum of '+ this.settings.maxChars  + ' characters';
                this.color = '#e75f63';
                return false;
            }else{
                return true;
            }
        },
        customValidators : function () {

            var err = 0;
            if(this.settings.minChars != ''){
                if(!(this.minChars())){
                    err++;
                }
            }

            if(this.settings.maxChars != ''){
                if(!(this.maxChars())){
                    err++;
                }
            }

            return err;
        }

    };

    $.fn[ pluginName ] = function ( options ) {
        this.each(function() {
            //if ( !$.data( this, "plugin_" + pluginName ) ) {
                $.data( this, "plugin_" + pluginName, new Plugin( this, options ) );
            //}
        });
        return this;
    };

})( jQuery, window, document );
