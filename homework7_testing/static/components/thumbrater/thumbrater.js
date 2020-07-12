(function () {

    var thumbrater = {
        props: ['url', 'callback_url'],
        data: null,
        methods: {}
    };

    thumbrater.data = function () {
        var data = {
            thumb_rating: 0,
            get_url: this.url,
            set_url: this.callback_url,
        };
        thumbrater.methods.load.call(data);
        return data;
    };

    thumbrater.methods.set_thumbs = function (star_idx) {
        // Sets and sends to the server the number of stars.
        let self = this;

        if (self.thumb_rating == null) {
            self.thumb_rating = star_idx;
        } else if (self.thumb_rating == star_idx) {
            self.thumb_rating = null;
        } else if (self.thumb_rating != null) {
            self.thumb_rating = star_idx;
        }

        axios.get(self.set_url,
            { params: { rating: self.thumb_rating } });
    };

    thumbrater.methods.load = function () {
        // In use, self will correspond to the data of the table,
        // as this is called via grid.methods.load
        let self = this;
        axios.get(self.get_url)
            .then(function (res) {
                self.thumb_rating = res.data.rating;
            })
    };

    utils.register_vue_component('thumbrater', 'components/thumbrater/thumbrater.html',
        function (template) {
            thumbrater.template = template.data;
            return thumbrater;
        });
})();

