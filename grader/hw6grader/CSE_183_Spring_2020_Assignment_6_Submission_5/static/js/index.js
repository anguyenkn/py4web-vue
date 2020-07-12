// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
        post_content: "",
        show_new_post: false,
        show_reply: null,
        author_name,
        user_email,
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
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
        }
        return a;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of app.vue.posts) {
            p._idx = i++;
        }
    };
    

    app.clear_new_post = () => {
        app.vue.post_content = "";
    }

    app.toggle_new_post = (toggle = !app.vue.show_new_post) => {
        app.clear_new_post();
        app.vue.show_reply = null;
        app.vue.show_new_post = toggle;
    }

    app.toggle_reply = (_idx) => {
        app.clear_new_post();
        app.vue.posts.forEach((post) => (post.edit = false));
        app.vue.show_new_post = false;
        app.vue.show_reply = _idx;
    };

    app.do_edit = (post_idx) => {
        // Handler for button that starts the edit.
        // TODO: make sure that no OTHER post is being edited.
        // If so, do nothing.  Otherwise, proceed as below.
        app.vue.posts.forEach((post) => (post.edit = false));
        app.vue.show_new_post = false;
        app.vue.show_reply = null;

        let p = app.vue.posts[post_idx];
        p.edit = true;
        p.is_pending = false;
    };

    app.do_cancel = (post_idx) => {
        // Handler for button that cancels the edit.
        let p = app.vue.posts[post_idx];
        p.edit = false;
        p.content = p.original_content;
    };
    //    if (p.id === null) {
    //       // If the post has not been saved yet, we delete it.
    //        app.vue.posts.splice(post_idx, 1);
    //        app.reindex();
    //    } else {
    //        // We go back to before the edit.
    //        p.edit = false;
    //        p.is_pending = false;
    //        p.content = p.original_content;
    //    }
    //}

    app.do_save = (post_idx) => {
        // Handler for "Save edit" button.
        let p = app.vue.posts[post_idx];
        if (p.content !== p.server_content) {
            p.is_pending = true;
            axios.post(posts_url, {
                content: p.content,
                id: p.id,
                is_reply: p.is_reply,
            }).then((result) => {
                console.log("Received:", result.data);
                p.original_content = p.content;
                p.server_content = p.content;
                p.edit = false;
            
                
                //adds posts locally onto screen
                //app.data.posts.unshift({
                //    id: result.data.id,
                //    edit: false,
                //    editable: true,
                //    content: result.data.content,
                //    server_content: result.data.content,
                //    original_content: "",
                //    author: null,
                //    email: null,
                //    is_reply: null,
                //})
                //app.reindex(app.data.posts);
            
                
            }).catch(() => {
                p.is_pending = false;
                console.log("Caught error");
                console.log(error)
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;
            p.original_content = p.content;
        }
    }

    app.fetch_posts = () => {
        axios
            .get(posts_url)
            .then((result) => {
                app.vue.posts = app.index(result.data.posts);
            })
            .catch((e) => {
                console.log(e);
            });
    };

    app.add_post = () => {
        // TODO: this is the new post we are inserting.
        // You need to initialize it properly, completing below, and ...
        if (app.vue.post_content.length == 0){
            return;
        }
        let q = {
            id: null,
            edit: false,
            editable: null,
            content: "",
            server_content: null,
            original_content: "",
            author: null,
            email: null,
            is_reply: null,
        };
        // TODO:
        // ... you need to insert it at the top of the post list.
        axios
        .post(posts_url, {
            id: null, 
            is_reply: null,
            content: app.vue.post_content,
        })
        .then((result) => {
            q = {
                ...q,
                id: result.data.id,
                editable: true,
                content: result.data.content,
                server_content: result.data.content,
                original_content: result.data.content,
                author: author_name,
                email: user_email,
            };
            app.vue.posts = [q, ...app.vue.posts];
            app.reindex();
            app.toggle_new_post(false);
        })
        .catch((e) => {
            console.log(e);
        });
    
    };

    app.reply = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id !== null) {
            // TODO: this is the new reply.  You need to initialize it properly...
            let q = {
                id: null,
                edit: null,
                editable: null,
                content: "",
                server_content: null,
                original_content: "",
                author: null,
                email: user_email,
                is_reply: null,
            };
            axios
                .post(posts_url, {
                    id: null,
                    is_reply: p.id,
                    content: app.vue.post_content,
                })
                .then((result) => {
                    q = {
                        ...q,
                        id : result.data.id,
                        editable : true,
                        content: result.data.content,
                        original_content: result.data.content,
                        server_content: result.data.content.
                        author: author_name,
                        email: user_email,
                        is_reply: p.id,
                    };
                    app.vue.posts.splice(post_idx + 1, 0, 1);
                    app.reindex();
                    app.toggle_reply(null);
                })
                .catch((e) => {
                    console.log(e);
                });
        }
    };

    app.do_delete = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // TODO:
            // If the post has never been added to the server,
            // simply deletes it from the list of posts.
            app.do_cancel(post_idx);
        } else {
            // TODO: Deletes it on the server.
            axios.post(delete_url, {id: p.id}).then((response) => {
                console.log(response);
                app.vue.posts.slice(post_idx, 1);
            }).catch((error) => {console.log(error)});
        };
        app.vue.posts = app.reindex(app.data.posts)
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
        toggle_new_post : app.toggle_new_post,
        toggle_reply: app.toggle_reply,
        blank_post: app.blank_post,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.fetch_posts();
    }
       
        

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
