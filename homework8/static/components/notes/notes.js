(function(){

    var notes = {
        props: ['url', 'callback_url'],
        data: null,
        methods: {}
    };

    notes.data = function() {
        var data = {
            rating: 0,
            get_url: this.url,
            set_url: this.callback_url
        };
        notes.methods.load.call(data);
        return data;
    }; 

    notes.methods.load = function () {
        let self = this;
        axios.get(self.get_url)
            .then(function(res) { 
                self.rating = res.data.rating;
                console.log(res)
            })
    };

    utils.register_vue_component('notes', 'components/notes/notes.html',
        function(template) {
            notes.template = template.data;
            return notes;
        });
})();