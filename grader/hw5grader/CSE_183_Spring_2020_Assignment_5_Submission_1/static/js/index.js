// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        user_first_name: user_first_name,
        user_last_name: user_last_name,
        posts: [], 
        show_add_post_form: false,
        text_empty: false,
        post_text: "",
    };

    // Add here the various functions you need.
    app.add_post_form = () => {
        app.vue.show_add_post_form = true;
    };
    
    app.hide_post_form = () => {
        app.vue.show_add_post_form = false;
    };
    
    app.make_post = () => {
        if (app.vue.post_text.trim().length === 0){
            app.vue.text_empty = true;
        }
        else {
            app.insert_post();
        }
        
    };
    
    app.insert_post = () => {
            
        axios.post(add_post_url, {
            user_email: app.vue.user_email,
            user_first_name: app.vue.user_first_name,
            user_last_name: app.vue.user_last_name,
            post_text: app.vue.post_text
            
        }).then( (response) => {
            app.vue.posts.unshift({
                    user_email: app.vue.user_email,
                    user_first_name: app.vue.user_first_name,
                    user_last_name: app.vue.user_last_name,
                    post_text: app.vue.post_text,
                    id: response.data.id,
                    rating: 0,
                    thumb_up: false,
                    thumb_down: false,
                    dislike_hover: false,
                    like_hover: false,
                    liked_by: [],
                    disliked_by: [],
                });
            app.reindex(app.vue.posts);
            app.vue.post_text = "";
            app.vue.text_empty = false;
            app.vue.show_add_post_form = false;
        });
    };

    app.delete_post = (post_idx) => {
        let p = app.vue.posts[post_idx];
        axios.post(delete_post_url, {id: p.id}).then( () => {
            app.vue.posts.splice(post_idx, 1);
            app.reindex(app.vue.posts);
        });
    };

    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        a.map((e) => {
            e._idx = idx++;
        });
    };
    
    app.complete = (posts) => {
        posts.map((post) =>{
            post.rating = 0;
            post.thumb_up = false;
            post.thumb_down = false;
            post.liked_by = [];
            post.disliked_by = [];
        });
    };
    
    app.thumb_out = (post_index) => {
        let post = app.vue.posts[post_index];
        if (post.rating == 1){
            post.thumb_up = true;
            post.thumb_down = false;
            post.like_hover=true;
            post.dislike_hover = false;
        } else if (post.rating == -1){
            post.thumb_up = false;
            post.thumb_down = true;
            post.like_hover=false;
            post.dislike_hover = true;
        } else{
            post.thumb_up = false;
            post.thumb_down = false;
            post.like_hover=false;
            post.dislike_hover = false;
        }
        
    };
    app.set_thumb = (post_index, rating) => {
        let p = app.vue.posts[post_index];
        if (rating == "up"){
            if (p.rating == 1){p.rating = 0;}
            else {p.rating = 1;}
        } else {
            if (p.rating == -1){p.rating=0;}
            else {p.rating = -1;}
        }
        app.thumb_out(post_index);
        axios.post(set_rating_url, {"post_id":p.id, "rating":p.rating});
        app.get_ratings(p, "up");
        app.get_ratings(p, "down");
    };
    
    app.thumb_up_over = (post_index) => {
        let post = app.vue.posts[post_index];
        post.thumb_up = true;
        post.like_hover = true;
        post.dislike_hover = false;
    };
    app.thumb_down_over = (post_index) => {
        let post = app.vue.posts[post_index];
        post.thumb_down = true;
        post.dislike_hover = true;
        post.like_hover = false;
    };
    
    app.get_ratings = (post, type) => {
        var rating_list = [];
        if (type == "up"){rating_list = post.liked_by;}
        else if (type == "down"){rating_list = post.disliked_by;}
        else {console.log("not editing any list"); return;}
        post_id = post.id;
        rating_list.splice(0, rating_list.length);
        axios.get(get_post_ratings_url, {params:{"post_id":post_id}}
            ).then((result) => {
                ratings = result.data.ratings;
                for (let r of ratings){
                    if (type == "up" && r.rating === 1){
                        axios.get(get_first_last_name_url, 
                                    {params: {"user_email":r.user_email}}
                            ).then( (result) => {
                                rating_list.push(result.data.name);
                            });
                    } else if (type == "down" && r.rating == -1) {
                        axios.get(get_first_last_name_url, 
                                    {params:{"user_email":r.user_email}}
                            ).then( (result) => {
                                rating_list.push(result.data.name);
                            });
                    }
                }
            });
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_post_form: app.add_post_form,
        hide_post_form: app.hide_post_form,
        make_post: app.make_post,
        insert: app.insert_post,
        delete_post: app.delete_post,
        thumb_out: app.thumb_out,
        set_thumb : app.set_thumb,
        thumb_up_over: app.thumb_up_over,
        thumb_down_over: app.thumb_down_over,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(get_posts_url).then((result) => {
            let posts = result.data.posts;
            app.complete(posts);
            app.reindex(posts);
            app.vue.posts = posts;
            app.data.posts = posts;
        }).then(() => {
            for (let p of app.vue.posts){
                axios.get(get_rating_url, {params:{"post_id": p.id}}
                ).then((result) => {
                    p.rating = result.data.rating;
                    if (p.rating == 1){
                        p.thumb_up = true;
                        p.like_hover = true;
                    } else if (p.rating == -1){
                        p.thumb_down = true;
                        p.dislike_hover=true;
                    }
                    app.get_ratings(p, "up");
                    app.get_ratings(p, "down");
                });
            }
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);