// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        posts: [],
        post_text: "",
        post_text_empty: false,
        show_add_field: false,
        thumb_click: false,
    };
    
    app.toggle_add_field = () => {
        app.vue.show_add_field = !app.vue.show_add_field;
    };

    app.check_post_text = () => {
        app.vue.post_text_empty = (app.vue.post_text.trim().length === 0);
    };

    // Add here the various functions you need.
    app.add_post = () => {
        let error = false;
        if (app.vue.post_text.trim().length === 0) {
            error = true;
            app.vue.post_text_empty = true;
        }
        if (!error) {
            app.toggle_add_field();
            app.perform_insertion();
        }
    };

    app.perform_insertion = () => {
        // We send the data to the server, from which we get the id.
        axios.post(add_post_url, {
            post_text: app.vue.post_text,
        }).then((response) => {
            app.vue.posts.unshift({
                id: response.data.id,
                user_email: user_email,
                post_text: app.vue.post_text,
                author: response.data.author,
                rating: 0,
            });
            // Reindex the posts
            app.reindex(app.vue.posts);
            // app.vue.posts = app.reindex(app.vue.posts)
            // ...and we blank the form.
            app.reset_form();
            app.init();
        });
    };

    app.delete_post = (post_idx) => {
        let post = app.vue.posts[post_idx];
        if (post.user_email == user_email) {
            axios.post(delete_post_url, {id: post.id}).then(() => {
                app.vue.posts.splice(post_idx, 1);
                app.reindex(app.vue.posts);
            });
        }
    };

    app.reset_form = () => {
        app.vue.post_text = ""
        app.vue.post_text_empty = false
    };

    app.cancel = () => {
        app.reset_form();
        app.toggle_add_field();
    };;

    app.set_rating = (post_id, rating, post_idx) => {
        app.vue.posts[post_idx].rating = rating;
        thumb_click = true;
        axios.post(set_rating_url, {post_id: post_id, rating: rating})
        .then(() => {
            app.mouse_enter(post_idx);
        });
    };

    app.mouse_enter = (post_idx) => {
        app.vue.posts[post_idx].show_likers = true;
        app.vue.posts[post_idx].show_dislikers = true;
        if(!app.vue.posts[post_idx].known_likers || thumb_click){
            app.get_likers(app.vue.posts[post_idx].id, post_idx)
            thumb_click = false;
        }
        else {
            if(app.vue.posts[post_idx].liker_string.length === 0)
                app.vue.posts[post_idx].show_likers = false;
            if(app.vue.posts[post_idx].disliker_string.length === 0)
                app.vue.posts[post_idx].show_dislikers = false;
        }
    };

    app.mouse_leave = (post_idx) => {
        app.vue.posts[post_idx].show_likers = false;
        app.vue.posts[post_idx].show_dislikers = false;
    };

    app.get_likers = (post_id, post_idx) => {
        axios.get(get_likers_url, {params: {"post_id": post_id}})
        .then((result) => {
            app.vue.posts[post_idx].liker_string = result.data.liker_string;
            app.vue.posts[post_idx].disliker_string = result.data.disliker_string;
            app.vue.posts[post_idx].known_likers = true;
        })
        .then(() => {
            if(app.vue.posts[post_idx].liker_string.length === 0)
                app.vue.posts[post_idx].show_likers = false;
            if(app.vue.posts[post_idx].disliker_string.length === 0)
                app.vue.posts[post_idx].show_dislikers = false;
        });
    }

    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (posts) => {
        let idx = 0;
        for (post of posts) {
            post._idx = idx++;
            post.show_likers = false;
            post.show_dislikers = false;
            post.liker_string = "";
            post.disliker_string = "";
            post.known_likers = false;
        }
        return posts;
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_post: app.add_post,
        check_post_text: app.check_post_text,
        cancel: app.cancel,
        toggle_add_field: app.toggle_add_field,
        delete_post: app.delete_post,
        set_rating: app.set_rating,
        mouse_enter: app.mouse_enter,
        mouse_leave: app.mouse_leave,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(get_posts_url)
        .then((result) => {
            app.vue.posts = app.reindex(result.data.posts);
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
