// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
		//is_any_post_in_edit_mode: false,
    };

    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            // TODO: Only make the user's own posts editable.
            p.editable = true; //user_email == p.email;	TODO==============
			p.readonly = "readonly"
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
	
    app.is_any_post_getting_edited = () => {

	    let returnValue = false;
        for (let p of app.vue.posts) 
		{
			//console.log(`NEEL edit value ${p.edit }`);
            if( p.edit == true)
			{
				return true;
			}
        }
        return returnValue;
    };	

    app.do_edit = (post_id) => {
        // Handler for button that starts the edit.
        // TODO: make sure that no OTHER post is being edited.
        // If so, do nothing.  Otherwise, proceed as below.
		if(app.is_any_post_getting_edited() == false)
		{
			//console.log("NEEL OK to edit");
			//console.log("NEEL OK to edit");
			
			post_index = app.post_id_to_index(post_id);
		
            let p = app.vue.posts[post_index];	
			p.edit = (p.editable == true) ? true : false;
			//app.vue.is_any_post_in_edit_mode = p.edit;
			p.is_pending = false;
		}
    };


	app.post_id_to_index = (post_id) => {
		let index = 0;
		 for (p of app.vue.posts) 
		 {
			 
			if(p.id == post_id)
			{
				return index;
			}
			index++;
		 }
		 return 0;
	};
	
    app.is_any_post_getting_edited = () => {

	    let returnValue = false;
        for (let p of app.vue.posts) 
		{
			//console.log(`NEEL edit value ${p.edit }`);
            if( p.edit == true)
			{
				return true;
			}
        }
        return returnValue;
    };
	


    app.do_cancel = (post_idx) => {
		
			app.repopulate_form();
    }
	
	

    app.do_save = (post_id) => {
		
		 //console.log(`Neel in do_save  js row id ${post_id} `);
		 
			 
		  
  		post_index = app.post_id_to_index(post_id);
		
        let p = app.vue.posts[post_index];	

		  axios.post(update_post_url, 
		  {   		
					post_id: p.id,
							content: p.content,
							title: p.title,
							//background_color: p.background_color,
							//rating: p.rating,			
		  
		  });
		  
		  app.repopulate_form();
		  


		 
    };	
	




    app.set_stars = function (post_id, new_rating) {
        // Sets and sends to the server the number of stars.
		//console.log("NEEL in set starts");
		//console.log(post_id);
		//console.log(new_rating);
		

		  axios.post(set_star_url, 
		  {   		
					post_id: post_id,
							rating: new_rating,			
		  
		  });
		  
		  app.repopulate_form();		
		
		
		
		
		

			
    };
	
    app.set_background = function (post_id, new_background) {

		//console.log("NEEL in set_background");
		//console.log(new_background);
        
		
		  axios.post(set_color_url, 
		  {   		
					post_id: post_id,
							background_color: new_background,			
		  
		  });
		  
		  app.repopulate_form();		
				
			
    };
	
    app.add_post = () => {
        // TODO: this is the new post we are inserting.
        // You need to initialize it properly, completing below, and ...
		//console.log("Neel add_post called");


        // We send the data to the server, from which we get the id.
		 axios.post(add_post_url, 
		 {
			content: "",
			title: "",
			background_color:"has-background-yellow-neel",
			rating: 1,        
			 
		 
		 })	
		 app.repopulate_form();				 


    };



    app.do_delete = (post_id) => {
	
		 if(confirm("Delete?") == false)
		 {
			return;
		 }
			console.log("Neel do_delete called");
			
            axios.post(delete_url, {   post_id: post_id,});
			
	
		app.repopulate_form();		
		
    };
	
   app.upload_file = function (event,post_id) {
	   
	    //console.log("NEELLLLLLLLLLLLLL upload file handler");
        // Reads the file.
        let input = event.target;
        let file = input.files[0];
		
	    //console.log("NEELLLLLLLLLLLLLL upload file handler");
			    //console.log(file);
		
        if (file) {
            let formData = new FormData();
            formData.append('file', file);
			formData.set('post_id',post_id);
            axios.post(image_url, formData,
                {headers: {'Content-Type': 'multipart/form-data'}})
                .then(function () {
                    console.log("Uploaded");
                })
                .catch(function () {
					alert("Failed to upload file, please select valid image file to upload");
                    console.log("Failed to upload");
                });
        }
    };	

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blo.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        do_delete: app.do_delete,
		set_stars: app.set_stars,	
		set_background: app.set_background,	
        upload_file: app.upload_file,		
		 
    };

 app.repopulate_form = () => {
        axios.get(posts_url).then((result) => {
			//app.vue.posts = []
			//if(result.data.posts.length > 0)
			{
				app.vue.posts = app.index(result.data.posts);
			}
        })		
    };	
	
    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
		
        // TODO: Load the posts from the server instead.
        // We set the posts.
		        axios.get(posts_url).then((result) => {
					
			app.vue.posts = app.index(result.data.posts);
			//console.log(app.vue.posts );
        })
   
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
