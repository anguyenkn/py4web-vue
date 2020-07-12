// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    app.data = {
        notes: [],
        adding_note: 0,
        new_title: "Title",
        new_content: "Take a note...",
    };

    app.index = (notes) => {
        let i = 0;
        for (let note of notes) {
            note.idx = i++;
            note.edit = false;
            note.original_content = note.content;
            note.server_content = note.content;
            note.original_title = note.title;
            note.server_title = note.title;
            note.display_buttons = 0;
            note.editing_image = 0;
            note.original_shared_email = note.shared_email;
            note.server_shared_email = note.shared_email;
            note.editing_sharing = 0;
        }
        return notes;
    };

    app.sort_notes = () => {
        app.vue.notes.sort((note1, note2) => (note1.last_modified > note2.last_modified) ? -1 : 1);
        app.vue.notes.sort((note1, note2) => (note1.star > note2.star) ? -1 : 1);
        app.reindex();
    };

    app.reindex = () => {
        let i = 0;
        for (let note of app.vue.notes) {
            note.idx = i++;
        }
    };

    app.do_edit = (idx) => {
        let note_to_edit = app.vue.notes[idx];
        for(note of app.vue.notes){
            if (note.id != note_to_edit.id){
                note.edit = false;
                app.do_cancel(note.idx);
            }
        }
        note_to_edit.edit = true;
    };

    app.do_cancel = (idx) => {
        let note = app.vue.notes[idx];
        console.log(app.vue.notes[idx])
        if (note.id === null) {
            app.vue.notes.splice(idx, 1);
            app.reindex();
        } else {
            note.edit = false;
            note.content = note.original_content;
            note.title = note.original_title;
        }
    }

    app.cancel_new_note = () => {
        app.vue.adding_note = 0;
        app.vue.new_title = "Title";
        app.vue.new_title = "Take a note...";
    }

    app.toggle_add_note = () => {
        app.vue.adding_note = 1;
    };

    app.do_save = (idx) => {
        let note = app.vue.notes[idx];
        console.log(note.shared_email)
        if (note.content !== note.server_content || note.title !== note.server_title || note.editing_image || note.editing_sharing) {
            axios.post(notes_url, {
                content: note.content,
                id: note.id,
                title: note.title,
                color: note.color,
                image_url: note.image_url,
                shared_email: note.shared_email,
            }).then((result) => {
                note.edit = false;
                console.log(result.data.id);
                note.id = result.data.id;
                note.original_content = result.data.content;
                note.server_content = result.data.content;
                note.last_modified = result.data.last_modified;
                note.shared_email = result.data.shared_email;
                note.server_shared_email = result.data.shared_email;
                note.original_shared_email = result.data.shared_email;
                app.sort_notes();
                note.editing_sharing = 0;
            })
        } else {
            note.edit = false;
            note.original_content = note.content;
            note.original_title = note.title;
        }
    };

    app.add_note = () => {
        app.vue.adding_note = 0;
        if (app.vue.new_title !== 'Title' || app.vue.new_content !== 'Take a note...') {
            let new_note = {
                id: null,
                edit: false,
                title: app.vue.new_title,
                content: app.vue.new_content,
                server_content: null,
                original_content: "",
                server_title: null,
                original_title: "",
                email: user_email,
                last_modified: null,
                color: 'dark',
                is_archived: 0,
                star: 0,
                display_buttons: 0,
                editing_image: 0,
                image_url: null,
                original_shared_email: "",
                server_shared_email: "",
                editing_sharing: 0,
            };
            axios.post(notes_url, {
                content: new_note.content,
                title: new_note.title,
                color: new_note.color,
            }).then((result) => {
                new_note.id = result.data.id;
                new_note.server_content = result.data.content;
                new_note.server_title = result.data.title;
                new_note.last_modified = result.data.last_modified;
                new_note.original_content = result.data.content;
                new_note.original_title = result.data.title;
                app.vue.notes.push(new_note);
                app.reindex();
                app.vue.new_title='Title';
                app.vue.new_content='Take a note...';
                app.sort_notes();
            })
        }
    };

    app.do_delete = (noteidx) => {
        let note_to_delete = app.vue.notes[noteidx];
        if (note_to_delete.id === null) {
            app.vue.notes.splice(noteidx, 1);
        } else {
            app.vue.notes.splice(noteidx, 1);
            axios.post(delete_url, {id:note_to_delete.id})
                .then((result) => {
                    console.log("deleted");
                    app.reindex();
            });
        }
    };

    app.set_color = (idx, color) => {
        let note = app.vue.notes[idx];
        console.log(note.idx)  
        axios.post(color_url, {
            color: color,
            id: note.id,
            star: note.star
        })
        .then((result) => {
            note.color = color;
            note.last_modified = result.data.last_modified;
            app.sort_notes();
        })
    };

    app.mouse_enter_handler = (idx) => {
        let note = app.vue.notes[idx];
        note.display_buttons = 1;
    }

    app.mouse_out_handler = (idx) => {
        let note = app.vue.notes[idx];
        note.display_buttons = 0;
    }

    app.toggle_star = (idx) => {
        let note = app.vue.notes[idx];
        note.star = note.star == 1 ? 0 : 1;
        app.set_color(idx, note.color);
        app.sort_notes();
        note.display_buttons = 0;
    }

    app.upload_file = function (event, idx) {
        let input = event.target;
        let note = app.vue.notes[idx]
        let file = input.files[0];
        if (file) {
            let formData = new FormData();
            formData.append('file', file);
            axios.post(upload_url, formData,
                {headers: {'Content-Type': 'multipart/form-data', 'id': note.id}})
                .then(function (result) {
                    console.log("Uploaded");
                    note.image_url = result.data.image_url;
                    note.last_modified = result.data.last_modified;
                    app.sort_notes();
                    note.editing_image = 0;
                })
                .catch(function () {
                    console.log("Failed to upload");
                });
        }
    };

    app.remove_image = (idx) => {
        let note = app.vue.notes[idx];
        note.image_url = null;
        app.do_save(idx);
        note.editing_image = 0;
    };

    app.toggle_image_edit = (idx) => {
        let note = app.vue.notes[idx];
        note.editing_image = note.editing_image == 1 ? 0 : 1;
    };

    app.save_shared_people = (idx) => {
        let note = app.vue.notes[idx];
        if (note.shared_email != note.original_shared_email){
            app.do_save(idx);
        }
        note.editing_sharing = 0;
    };

    app.toggle_share_edit = (idx) => {
        let note = app.vue.notes[idx];
        note.editing_sharing = note.editing_sharing === 1 ? 0 : 1;
        if (note.shared_email != note.original_shared_email)
            note.shared_email = note.original_shared_email;
        console.log('here')
    };

    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_note: app.add_note,
        do_delete: app.do_delete,
        set_color: app.set_color,
        cancel_new_note: app.cancel_new_note,
        toggle_add_note: app.toggle_add_note,
        mouse_enter_handler: app.mouse_enter_handler,
        mouse_out_handler: app.mouse_out_handler,
        toggle_star: app.toggle_star,
        upload_file: app.upload_file,
        remove_image: app.remove_image,
        toggle_image_edit: app.toggle_image_edit,
        save_shared_people: app.save_shared_people,
        toggle_share_edit: app.toggle_share_edit,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(notes_url)
        .then((result) => {
            app.vue.notes = app.index(result.data.notes);
            app.sort_notes();
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
