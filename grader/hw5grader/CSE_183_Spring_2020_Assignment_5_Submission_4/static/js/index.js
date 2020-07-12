// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
// CODE ADAPTED FROM TA SESSION: Matan Broner 5/11 5/12 
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        posts: [], // Suggested.
        post_text: "",
        new_post_showing: false,
        hover_post: null,
        // Complete.
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        // Complete.
        send_post: app.send_post,
        delete_post: app.delete_post,
        send_thumb:app.send_thumb,
        toggle_new_post: app.toggle_new_post,
        clear_new_post: app.clear_new_post,
        user_thumb_on_post: app.user_thumb_on_post,
        toggle_hover_post: app.toggle_hover_post,
    };

    // Add here the various functions you need.


    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
            // Add here whatever other attributes should be part of a post.
        }
        return a;
    };


    // need to force refresh the page so that the likes and dislike buttons will be updated
    app.refresh = () => {
        let temp = app.vue.hover_post;
        app.vue.hover_post = null;
        app.vue.hover_post = temp;
    }


    // vue function to check whether the post is being hovered on
    app.toggle_hover_post = (post_id) => {
        app.vue.hover_post = post_id;
    }

    app.format_post_thumbs = (post) => {
        post.likes = [];
        post.dislikes = []; 
        post.thumbs.forEach((thumb) => {
            let info = {
                name: thumb.name,
                user_email: thumb.user_email, 
            };
            if(thumb.rating == 1) {
                post.likes.push(info);
            } else if (thumb.rating == -1) {
                post.dislikes.push(info);
            }
        });
        return post;
    };

    app.user_thumb_on_post = (post, rating) => {
        if(rating === 0) {
            return false;
        } else {
            let arr;
            if (rating === 1) {
                arr = post.likes;
            }else {
                arr = post.dislikes;
            }
            let index = arr.findIndex((user) => user.user_email === user_email);
            return index !== -1;
        }
    };


    app.send_post = () => {
        axios
        .post(add_post_url, { post_text: app.vue.post_text })
        .then((result) => {
            let post = app.format_post_thumbs(result.data.post);
            app.vue.posts = app.reindex([post, ...app.vue.posts]);
            app.clear_new_post();
        })
        .catch((e) => alert("Error Sending new Post:", e));

    };


    app.send_thumb = (post_id, rating) => {
        axios
        .post(thumb_post_url, {
            post_id,
            rating,
        })
        .then((result) => {
            let post = app.format_post_thumbs(result.data.post);
            let index = app.vue.posts.findIndex((post) => post.id === post_id);
            app.vue.posts[index] = post;
            app.vue.posts = app.reindex(app.vue.posts);
            app.refresh();
        });
    };


    app.toggle_new_post = () => {
        app.vue.new_post_showing = !app.vue.new_post_showing;
    };

    app.clear_new_post = () => {
        app.vue.post_text = "";
    };


    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.get_posts = () => {
        axios
            .get(get_posts_url)
            .then((result) => {
                let posts = result.data.posts.map((post) => app.format_post_thumbs(post));
                app.vue.posts = app.reindex(posts);
            })
            .catch((e) => alert("Error Getting New Post:", e));
    };

    app.delete_post = (post_id) => {
        axios
            .post(delete_post_url, {
             post_id,
            })
            .then(() => {
             app.vue.posts = app.vue.posts.filter((post) => post.id !== post_id);
        });
    };


    // And this initializes it.
    app.init = () => {
        app.get_posts();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
