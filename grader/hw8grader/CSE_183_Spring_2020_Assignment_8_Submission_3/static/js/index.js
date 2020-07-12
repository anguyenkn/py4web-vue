// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        notes: [],
        add_note_text: "",
        add_note_title: "",
        note_text_empty: false,
        textbox: "notShown",
    };
    
    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            // TODO: Only make the user's own posts editable.
            p.editable = true;
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_note_text = p.note_text; // Content before an edit.
            p.server_note_text = p.note_text;
            p.original_note_title = p.note_title; // Content before an edit.
            p.server_note_title = p.note_title;// Content on the server.
        }
        return a;
    };
    
    app.add_note = () => {
        let error = false;
        if (app.vue.add_note_text.trim().length === 0) {
            //error = true;
            app.vue.note_text_empty = true;
        }
        if (app.vue.add_note_title.trim().length === 0) {
            //error = true;
            app.vue.note_text_empty = true;
        }
        if (!error) {
            // We perform the actual insertion.
            app.perform_insertion();
            app.init()
        }
    };
    
    app.perform_insertion = () => {
        // We send the data to the server, from which we get the id.
        axios.post(add_note_url, {
            note_text: app.vue.add_note_text,
            note_title: app.vue.add_note_title,
        }).then(function (response) {
            // We add the person in the input form...
            app.vue.notes.push({
                id: response.data.id,
                note_text: app.vue.add_note_text,
                note_title: app.vue.add_note_title,
            });
            // We re-enumerate the rows.
            app.reindex(app.vue.notes);
            // ...and we blank the form.
            app.reset_text();
            app.textboxChange('notShown');
        });
    };
    
    app.do_edit = (note_idx) => {

        app.vue.notes.forEach((note) => (note.edit = false));
        let p = app.vue.notes[note_idx];
        p.edit = true;
        p.is_pending = false;
    };
    
    app.do_cancel = (note_idx) => {
        let p = app.vue.notes[note_idx];
        p.edit = false;
        p.note_text = p.original_note_text;
        p.note_title = p.original_note_title;
    }
    
    app.do_save = (note_idx) => {
        // Handler for "Save edit" button.
        let p = app.vue.notes[note_idx];
        if (p.note_text !== p.server_note_text || p.note_title !== p.server_note_title) {
            p.is_pending = true;
            axios.post(save_note_url, {
                note_text: p.note_text,
                note_title: p.note_title,
                id: p.id,
            }).then((result) => {
                console.log("Received:", result.data);
                p.original_note_text = p.note_text;
                p.server_note_text=p.note_text;
                p.original_note_title = p.note_title;
                p.server_note_title=p.note_title;
                p.edit=false;
            }).catch((e) => {
                p.is_pending = false;
                console.log(e);
                // We stay in edit mode.
            });
            
        } else {
            // No need to save.
            p.edit = false;
            p.original_note_text = p.note_text;
            p.original_note_title = p.note_title;
        }
    }
    
    app.delete_note = (note_idx) => {
        // First, we figure out the persons we are deleting from the _idx.
        // _idx is added by the call to app.enumerate in app.init.
        let p = app.vue.notes[note_idx];
        // Then, we call to delete that specific id.
        axios.post(delete_note_url, {id: p.id}).then(() => {
            // The deletion went through on the server. Deletes also locally.
            // Isn't it obvious that splice deletes an element?  Such is life.
            app.vue.notes.splice(note_idx, 1);
            app.reindex(app.vue.notes);
            app.init()
        })
    };
    
    
    app.check_note_text = () => {
        app.vue.note_text_empty = (app.vue.add_note_text.trim().length === 0 && app.vue.add_note_title.trim().length === 0);
    };
    
    app.textboxChange = (destination) => {
        app.reset_text();
        app.vue.textbox = destination;
    };
    
    app.reset_text = () => {
        app.vue.note_text_empty = false;
        app.vue.add_note_text = "";
        app.vue.add_note_title = "";
    };
    
    app.fetch_notes=()=>{
        axios
        .get(get_notes_url)
        .then((result) =>{
            app.vue.notes = app.index(result.data.notes);
            app.vue.notes = app.reindex(result.data.notes);
        })
        .catch((e) => {;
            console.log(e)
        });
    }

    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
        }
        return a;
    };
    
    app.complete = (notes) => {
        // Initializes useful fields of images.
        notes.map((ps) => {
            if(ps.shade != 2 || ps.shade != 3 || ps.shade != 4 || ps.shade != 5 || ps.shade != 6){
                ps.shade = 1;
            }
            if(ps.star != 1){
                ps.star = 0;
            }
        })
    };
    
    app.set_color = (ps_idx, shade) => {
        let ps = app.vue.notes[ps_idx];
        ps.shade = shade;
        // Sets the stars on the server.
        axios.post(set_shade_url, {note_id: ps.id, shade: shade});
    };
    
    app.set_star = (ps_idx, star) => {
        let ps = app.vue.notes[ps_idx];
        ps.star = star;
        // Sets the stars on the server.
        axios.post(set_star_url, {note_id: ps.id, star: star});
    };
    

    app.methods = {
        set_color: app.set_color,
        set_star: app.set_star,
        delete_note: app.delete_note,
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        textboxChange: app.textboxChange,
        add_note: app.add_note,
        check_note_text: app.check_note_text,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        axios.get(get_notes_url).then((result) => {
            let notes = result.data.notes;
            app.index(notes);
            app.complete(notes);
            app.vue.notes = notes;
        })
        .then(() => {
                for (let ps of app.vue.notes) {
                    axios.get(get_shade_url, {params: {"note_id": ps.id}})
                        .then((result) => {
                            ps.shade = result.data.shade;
                        });
                    axios.get(get_star_url, {params: {"note_id": ps.id}})
                        .then((result) => {
                            ps.star = result.data.star;
                        });
                }
        });
    };

    app.init();
};

init(app);
