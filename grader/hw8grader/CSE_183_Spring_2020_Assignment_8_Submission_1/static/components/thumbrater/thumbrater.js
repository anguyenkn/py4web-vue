(function(){

    var thumbrater = {
        props: ['url', 'callback_url'],
        data: null,
        methods: {}
    };

    thumbrater.data = function() {
        var data = {
            thumbs_display: 0,
            rating: 0,
            get_url: this.url,
            set_url: this.callback_url,
        };
        thumbrater.methods.load.call(data);
        return data;
    };

    thumbrater.methods.set_thumbs = function (rating) {
        // Sets and sends to the server the number of stars.
        let self = this;
        self.rating = rating;
        self.thumbs_display = rating
        axios.get(self.set_url,
            {params: {rating: self.rating}}).then(function (res) {
                console.log("resul of set: ", res)
        });
    };

    thumbrater.methods.load = function () {
        // In use, self will correspond to the data of the table,
        // as this is called via grid.methods.load
        console.log("loading stuff")
        let self = this;
        axios.get(self.get_url)
            .then(function(res) {
                console.log("res: ", res)
                self.rating = res.data.rating;
                self.thumbs_display = res.data.rating;
            })
    };

    utils.register_vue_component('thumbrater', 'components/thumbrater/thumbrater.html',
        function(template) {
            thumbrater.template = template.data;
            return thumbrater;
        });
})();
