// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        notes: [] //notes = [pinned, sort=desc(notes.pinned)] + [unpinned]
    };

    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        for (let p of a) {
            p._idx = app.vue.counter++;
            // Add here whatever other attributes should be part of a post.
        }
        return a;
    };

    app.insertUnpinned = (notes, note) => {
        for (let i = 0; i < notes.length; i++)
            if (note.note_date > notes[i].note_date && notes[i].pinned == 0) {
                notes.splice(i, 0, note);
                return;
            }
        notes.push(note);
    }

    app.delete_note = (id, index, edit_status) => {
        if (edit_status === -1)
            app.vue.notes.splice(index, 1);
        else
            axios.post(delete_note_url, {id: id}).then(() => {
                app.vue.notes.splice(index, 1);
            });
    };

    app.add_note = () => {
        let note = {
            id: null,
            title: '',
            content: '',
            note_date: Date.now(),
            color: 'is-white',
            pinned: 0, // position in pinned subset if (pinned > 0)
            edit: -1   // -1 if post hasn't been posted to db yet
        };
        app.insertUnpinned(app.vue.notes, note)
    };

    app.insert_pinned = function (note, index) {
        if (!note.pinned) { // insert into pinned subset
            note.pinned = app.vue.notes[0] ? app.vue.notes[0].pinned + 1 : 1;
            app.vue.notes.unshift(app.vue.notes.splice(index, 1)[0]);
        } else {//insert into unpinned subset
            app.insertUnpinned(app.vue.notes, app.vue.notes.splice(index, 1)[0])
            note.pinned = 0;
        }
    };

    // Vue instance methods
    app.methods = {
        delete_note: app.delete_note,
        add_note: app.add_note,
        insert_pinned: app.insert_pinned
    };

    //Creates Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    //Init Vue instance
    app.init = () => {
        axios.get(notes_url).then((response) => {
            let pinned = response.data.notes.filter(note => note.pinned > 0).sort((a, b) => b.pinned - a.pinned);
            let unpinned = response.data.notes.filter(note => note.pinned == 0).reverse();
            app.vue.notes = pinned.concat(unpinned);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
