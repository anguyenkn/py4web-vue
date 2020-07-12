// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Rows for the table.
        // Initially empty, it is then filled via the app.init method.
        rows: [],
        // These fields are connected to the input form via v-model.
        // When the user changes the value in the input, these fields are
        // updated as well.
        add_first_name: "",
        add_last_name: "",
        first_name_empty: false,
        last_name_empty: false,
        page: "list", // Used to decide which page to show.
    };

    app.enumerate = (a) => {
        // This is a convenience function that adds a _idx field
        // to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.add_person = () => {
        let error = false;
        if (app.vue.add_first_name.trim().length === 0) {
            error = true;
            app.vue.first_name_empty = true;
        }
        if (app.vue.add_last_name.trim().length === 0) {
            error = true;
            app.vue.last_name_empty = true;
        }
        if (!error) {
            // We perform the actual insertion.
            app.perform_insertion();
        }
    };

    app.perform_insertion = () => {
        // We send the data to the server, from which we get the id.
        axios.post(add_person_url, {
            first_name: app.vue.add_first_name,
            last_name: app.vue.add_last_name,
        }).then(function (response) {
            // We add the person in the input form...
            app.vue.rows.push({
                id: response.data.id,
                first_name: app.vue.add_first_name,
                last_name: app.vue.add_last_name
            });
            // We re-enumerate the rows.
            app.enumerate(app.vue.rows);
            // ...and we blank the form.
            app.reset_form();
            app.goto('list');
        });
    };

    app.reset_form = () => {
        app.vue.first_name_empty = false;
        app.vue.last_name_empty = false;
        app.vue.add_first_name = "";
        app.vue.add_last_name = "";
    };

    // These two functions are triggered whenever there is a change to
    // the inputs, and they set the error flag according to whether the
    // input field is empty.  Without these, the error does not disappear
    // when one enters text.
    app.check_first_name = () => {
        app.vue.first_name_empty = (app.vue.add_first_name.trim().length === 0);
    };

    app.check_last_name = () => {
        app.vue.last_name_empty = (app.vue.add_last_name.trim().length === 0);
    };

    app.delete_person = (person_idx) => {
        // First, we figure out the person we are deleting from the _idx.
        // _idx is added by the call to app.enumerate in app.init.
        let p = app.vue.rows[person_idx];
        // Then, we call to delete that specific id.
        axios.post(delete_person_url, {id: p.id}).then(() => {
            // The deletion went through on the server. Deletes also locally.
            // Isn't it obvious that splice deletes an element?  Such is life.
            app.vue.rows.splice(person_idx, 1);
            app.enumerate(app.vue.rows);
        })
    };

    app.goto = (destination) => {
        app.vue.page = destination;
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_person: app.add_person,
        check_first_name: app.check_first_name,
        check_last_name: app.check_last_name,
        delete_person: app.delete_person,
        goto: app.goto,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    // Generally, this will be a network call to the server to
    // load the data.
    // For the moment, we 'load' the data from a string.
    app.init = () => {
        // We load the rows from the server, using the axios library.
        // See https://github.com/axios/axios
        axios.get(load_rows_url).then(function (response) {
            // response.data contains the response.
            // response has other fields, such as status, etc; see them in the log.
            console.log(response);
            app.vue.rows = app.enumerate(response.data.rows);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
