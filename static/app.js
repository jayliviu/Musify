// ******************************************* Playlist Functions ********************************************

$('#show-playlist-row').on('click', '.delete', async function(e) {

   const $playlistContainer = $(e.target).parent().parent().parent();

   const $playlistId = $playlistContainer.attr('data-playlist_id');

   const response = await axios.delete(`/playlists/${$playlistId}`);

   if(response.data.status == 'success'){
      $playlistContainer.remove();
   }

});



$('#create-playlist-form').on('submit', async function(e) {

   e.preventDefault();

   const $form = $('#create-playlist-form');

   const $playlistName = $('#playlist-form-input').val();

   const $user = $form.data('user_id');

   const response = await axios.post(`/playlists`, {playlist_name:$playlistName, user_id:$user});

   if(response.data.status == 'success'){

      let playlistId = response.data.playlist.id;

      let playlistName = response.data.playlist.name;

      let dateCreated = response.data.playlist.date_created;

      let userId = response.data.playlist.user_id;

      let user = response.data.user;

      const $showPlaylistRow = $('#show-playlist-row');

      const htmlString = `
      <div class="col-12 border border-dark rounded mb-1 playlist-container" data-playlist_id=${playlistId} style="background-color:rgb(216, 131, 255);">
         <h2 class="text-center text-dark font-weight-bolder font-italic mt-2 playlist-header"> ${user.display_name} - ${playlistName}</h2>
         <hr class="mt-1 mb-2 mx-5">
         <p class="text-center text-dark font-italic date-created">Date Created : ${dateCreated.slice(0,10)}</p>
         <div class="row d-flex justify-content-center align-items-center">
            <div class="col-5 m-2">
               <button class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark view" style="background-color: #9198e5">View</button>   
            </div>
            <div class="col-5 m-2">
               <button class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark delete" style="background-color: #9198e5"">Delete</button>   
            </div>
         </div>
      </div>
      `;

      $showPlaylistRow.append(htmlString);
   };

   $form.trigger('reset');

});



$('#spotify-search-row').on('click', '.playlist-add', async function(e) {

   const response = await axios.get(`/playlists/data`)

   if(response.data.status == 'success') {

      const $spotifySongContainer = $(e.target).parent().parent().parent()

      const trackName = $spotifySongContainer.data('track_name')

      const userId = $spotifySongContainer.data('user_id')

      const trackSpotifyUri = $spotifySongContainer.data('track_spotify_uri')

      const trackSpotifyId = $spotifySongContainer.data('track_spotify_id')

      let trackArtistName = $spotifySongContainer.data('artist_name')

      const trackArtistUrl = $spotifySongContainer.data('artist_url')

      const $spotifySearchRow = $('#spotify-search-row')

      $spotifySearchRow.data('track_name', trackName)

      $spotifySearchRow.data('track_spotify_uri', trackSpotifyUri)

      $spotifySearchRow.data('track_spotify_id', trackSpotifyId)

      $spotifySearchRow.data('artist_name', trackArtistName)

      $spotifySearchRow.data('artist_url', trackArtistUrl)

      $spotifySearchRow.data('user_id', userId)

      $('.spotify-song-container').remove()

      const user = response.data.user

      for(let playlist of response.data.playlists) {

         const htmlString = `
         <div class="col-12 border border-dark rounded mb-1 playlist-container" data-user_id="${user.id}" data-playlist_id="${playlist.id}" data-playlist_name="${playlist.name}" style="background-color:rgb(216, 131, 255);">
            <h2 class="text-center text-dark font-weight-bolder font-italic mt-2"> ${user.display_name} - ${playlist.name}</h2>
            <hr class="mt-1 mb-2 mx-5">
            <p class="text-center text-dark font-italic date-created">Date Created : ${playlist.date_created.slice(0,10)}</p>
            <div class="row d-flex justify-content-center align-items-center">
               <div class="col-5 m-2">
                  <button class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark add" style="background-color: #9198e5">Add</button>   
               </div>
               <div class="col-5 m-2">
                  <form action="/search">
                     <button type="submit" class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark back" style="background-color: #9198e5">Back to Search</button>   
                  </form>
               </div>
            </div>
         </div>
         `;

         $spotifySearchRow.append(htmlString)

      }
      const track_liked_response = await axios.post(`/tracks`, {track_name:trackName, track_id:trackSpotifyId, track_uri:trackSpotifyUri, track_artist_name:trackArtistName, track_artist_url:trackArtistUrl, user_id:userId})
   
      $spotifySearchRow.data('track_id', track_liked_response.data.track)
   };


});

$('#spotify-search-row').on('click', '.add', async function(e) {

   const $playlistContainer = $(e.target).parent().parent().parent();

   const playlistId = $playlistContainer.data('playlist_id');

   const trackId = $('#spotify-search-row').data('track_id')

   const playlist_track_response = await axios.post(`/add/playlists/tracks`, {track_id:trackId, playlist_id:playlistId});

   if(playlist_track_response.data.status == 'success'){
      $(this).remove()
   };

});   


$('#show-playlist-row').on('click', '.view', async function(e) {

   const $playlistContainer = $(e.target).parent().parent().parent();

   const $playlistId = $playlistContainer.attr('data-playlist_id');
   
   const response = await axios.get(`/playlists/${$playlistId}/tracks`);

   if(response.data.status == 'success'){
   
      $('.playlist-container').remove();

      const $showPlaylistRow = $('#show-playlist-row');

      for(let track of response.data.tracks) {

         const trackId = track.id;

         const trackName = track.name;

         const trackSpotifyId = track.spotify_id;

         const trackSpotifyUri = track.spotify_uri;

         const trackDateLiked = track.date_liked;

         const trackArtistName = track.artist_name;

         const trackArtistUrl = track.artist_url;

         const htmlString = `

            <div class="col-12 border border-dark rounded mb-1 playlist-tracks-container" data-track_id="${trackId}" data-track_spotify_id="${trackSpotifyId}" data-track_spotify_uri="${trackSpotifyUri}" style="background-color:rgb(216, 131, 255);">
               <h2 class="text-center text-dark font-weight-bolder font-italic mt-2 playlist-header"> ${trackArtistName} - ${trackName}</h2>
               <hr class="mt-1 mb-2 mx-5">
               <p class="text-center text-dark font-italic date-liked">Date Liked : ${trackDateLiked.slice(0,10)}</p>
               <div class="row d-flex justify-content-center align-items-center">
                  <div class="col-5 m-2">
                     <form action="/search">
                        <button type="submit" class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark back" style="background-color: #9198e5">Back to Search</button>   
                     </form>   
                  </div>
                  <div class="col-5 m-2">
                     <form action="/playlists" method="GET">
                        <button type="submit" class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark back" style="background-color: #9198e5">Back to Playlist</button>   
                     <form/>
                  </div>
               </div>
            </div>

         `;

         $showPlaylistRow.append(htmlString);
      };
   };
});



$('#search-date-form').on('submit', async function(e) {

   e.preventDefault();

   const $form = $('#search-date-form');

   const $dateInputValue = $('#search-date-input').val();

   const $user = $form.data('user_id');

   const response = await axios.post(`/tracks/date`, {user_id:$user, date_liked:$dateInputValue});

   if(response.data.status == 'success'){

      $('.liked-track-container').remove()

      const $showTracksRow = $('#show-tracks-row');

      for(let track of response.data.tracks){

         const trackId = track.id;

         const trackName = track.name;

         const trackSpotifyId = track.spotify_id;

         const trackSpotifyUri = track.spotify_uri;

         const trackDateLiked = track.date_liked;

         const trackArtistName = track.artist_name;

         const trackArtistUrl = track.artist_url;

         const htmlString = `
            <div class="col-12 border border-dark rounded mb-1 dated-track-container" data-track_id="${trackId}" data-track_spotify_id="${trackSpotifyId}" data-track_spotify_uri="${trackSpotifyUri}" style="background-color:rgb(216, 131, 255);">
               <h2 class="text-center text-dark font-weight-bolder font-italic mt-2 playlist-header"> ${trackArtistName} - ${trackName}</h2>
               <hr class="mt-1 mb-2 mx-5">
               <p class="text-center text-dark font-italic date-liked">Date Liked : ${trackDateLiked.slice(0,10)}</p>
               <div class="row d-flex justify-content-center align-items-center">
                  <div class="col-5 m-2">
                     <form action="/search">
                        <button type="submit" class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark listen" style="background-color: #9198e5">Back to Search</button>   
                     </form>
                  </div>
                  <div class="col-5 m-2">
                     <form action="/tracks" method="GET">
                        <button type="submit" class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark back" style="background-color: #9198e5">Back to Likes</button>   
                     <form/>
                  </div>
               </div>
            </div>
         `;

         $showTracksRow.append(htmlString)
      };
   }
   $form.trigger('reset')
});



$('#search-spotify-form').on('submit', async function(e) {

   e.preventDefault();

   $('.spotify-song-container').remove()

   const $form = $('#search-spotify-form');

   const $inputValue = $("#search-spotify-input").val();

   const response = await axios.post('/search', {value:$inputValue});

   if(response.data.status == 'success') {

      const $spotifySearchRow = $('#spotify-search-row');

      for(let item of response.data.items) {

         const htmlString = `

         <div class="col-12 border border-dark rounded mb-1 spotify-song-container" data-user_id="${response.data.user.id}" data-track_name="${item.name}" data-track_spotify_uri="${item.uri}" data-track_spotify_id="${item.id}" data-artist_name="${item.artists[0].name}" data-artist_url="${item.artists[0].external_urls.spotify}" style="background-color:rgb(216, 131, 255);">
         <h2 class="text-center text-dark font-weight-bolder font-italic mt-2"> ${item.artists[0].name} - ${item.name}</h2>
         <hr class="mt-1 mb-2 mx-5">
         <p class="text-center text-dark font-italic popularity">Popularity: ${item.popularity}</p>
            <div class="row d-flex justify-content-center align-items-center">
               <div class="col-4 m-1">
                  <button class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark listen" style="background-color: #9198e5">Listen</button>   
               </div>
               <div class="col-3 m-1">
                  <button class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark playlist-add" style="background-color: #9198e5">Add to Playlist</button>   
               </div>
               <div class="col-4 m-1">
                  <button class="btn btn-block btn-block-lg font-weight-bolder font-italic p-1 text-dark like" style="background-color: #9198e5">Like</button>
               </div>
            </div>
         </div>
         `;

         $spotifySearchRow.append(htmlString);
      
      };
   };

   window.onSpotifyIframeApiReady = (IFrameAPI) => {
      $('.embed-iframe-container').hide()
      const element = document.getElementById('embed-iframe');
      const options = {
         uri: ''
      };
      const callback = (EmbedController) => {
         $('#spotify-search-row').on('click', '.listen', function(e) {

            $('.embed-iframe-container').show()

            const $parentContainer = $(e.target).parent().parent().parent()

            EmbedController.loadUri($parentContainer.data('track_spotify_uri'))
         });
      };
      IFrameAPI.createController(element, options, callback);
   };

   $('.like').on('click', async function(e) {

      const $trackContainer = $(this).parent().parent().parent();
      
      const trackName = $trackContainer.data('track_name');
   
      const trackId = $trackContainer.data('track_spotify_id');
   
      const trackUri = $trackContainer.data('track_spotify_uri');
   
      const trackArtistName = $trackContainer.data('artist_name');
   
      const trackArtistUrl = $trackContainer.data('artist_url');
   
      const user = $trackContainer.data('user_id');
   
      const response = await axios.post(`/tracks`, {track_name:trackName, track_id:trackId, track_uri:trackUri, track_artist_name:trackArtistName, track_artist_url:trackArtistUrl, user_id:user});
   
   });

   $form.trigger('reset');
});



$('.unlike').on('click', async function(e) {

   const $trackContainer = $(this).parent().parent().parent();

   const $trackId = $trackContainer.data('track_id');

   const response = await axios.delete(`/tracks/${$trackId}`);

   if(response.data.status == 'success'){
      $trackContainer.remove();
   };

});
