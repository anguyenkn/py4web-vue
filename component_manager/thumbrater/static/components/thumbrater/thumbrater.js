(function(){

    var thumbrater = {
        props: ['url', 'callback_url'],
        data: null,
        methods: {}
    };

    thumbrater.data = function() {
        var data = {
            rating: 0,
            get_url: this.url,
            set_url: this.callback_url
        };
        thumbrater.methods.load.call(data);
        return data;
    };

    thumbrater.methods.set_thumb = function (rating) {
        if (this.rating === rating)
            rating = 0
        axios.get(this.set_url,
            {params: {rating: rating}})
            .then(() => {
                this.rating = rating;
            })
    };

    thumbrater.methods.load = function () {
        let self = this;
        axios.get(self.get_url)
            .then(function(res) {
                self.rating = res.data.rating;
                console.log(res)
            })
    };

    utils.register_vue_component('thumbrater', 'components/thumbrater/thumbrater.html',
        function(template) {
            thumbrater.template = template.data;
            return thumbrater;
        });
})();