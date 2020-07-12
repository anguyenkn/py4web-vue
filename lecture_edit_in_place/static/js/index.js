// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        abstract: "",
        edit: false,
        is_pending: false,
        error: false,
        original_abstract: "", // Original abstract before edit.
        server_abstract: "", // Abstract as on the server.
    };

    app.sleep = (ms) => {
        return function (x) {
            return new Promise(resolve => setTimeout(() => resolve(x), ms));
        };
    }

    app.do_edit = () => {
        // Handler for button that starts the edit.
        app.vue.edit = true;
        app.vue.is_pending = false;
    };

    app.do_cancel = () => {
        // Handler for button that cancels the edit.
        app.vue.edit = false;
        app.vue.is_pending = false;
        app.vue.abstract = app.vue.original_abstract;
    }

    app.do_save = () => {
        // Handler for "Save edit" button.
        if (app.vue.abstract !== app.vue.server_abstract) {
            app.vue.is_pending = true;
            axios.post(callback_url, {abstract: app.vue.abstract})
                .then((result) => {
                    console.log("Saved:", result.data.abstract)
                    app.vue.edit = false;
                    app.vue.original_abstract = app.vue.abstract;
                    app.vue.server_abstract = result.data.abstract;
                    app.vue.is_pending = false;
                })
                .catch(() => {
                    app.show_error();
                });
        }
    }

    app.show_error = () => {
        // Flashes an error if an error occurred.
        app.vue.error = true;
        app.vue.is_pending = false;
        app.sleep(2000)()
            .then(() => {
                app.vue.error = false;
                app.vue.edit = true;
            });
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    // In a realistic setting we would need to do a server call.
    app.init = () => {
        app.vue.abstract = "";
        app.vue.original_abstract = "";
        app.vue.server_abstract = "";
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
