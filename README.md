# Musify

Musify is a full-stack web application that replicates core functionalities of Spotify. The application uses the Spotify API to let users search for songs, manage playlists, and save their favorite tracks. Built using **Python**, **Flask**, **SQLAlchemy**, and **PostgreSQL** on the backend, along with **JavaScript**, **jQuery**, and **Bootstrap 4** on the frontend, this project adheres to RESTful API standards.

## Key Features

### **User Authentication**
- **Sign Up**: Users can create an account with a username and password. Passwords are securely hashed using **bcrypt** before being stored in the database.
- **Login & Logout**: Session management is implemented using Flask sessions. Upon login, users are greeted with a personalized message and redirected to the search page.
- **Spotify Authorization**: OAuth2 is used to authorize users' Spotify accounts. The app fetches and stores user profile information, including their Spotify ID, display name, and profile picture, into the database.

### **Spotify Integration**
- **Access & Refresh Tokens**: After receiving an authorization code from Spotify, the app exchanges it for an access token and refresh token. Tokens are saved with expiration timestamps, and expired access tokens are refreshed automatically to ensure seamless user interactions.
- **Search Songs**: Users can search Spotify's catalog for tracks. Search results, including song names, artists, and links, are displayed dynamically using **Axios** requests and rendered in real-time on the frontend.
- **Profile Synchronization**: Profile details fetched from Spotify are stored in the app's database, allowing users to access their Spotify information directly within Musify.

### **Playlist and Track Management**
- **Liked Tracks**: Users can save tracks they enjoy. Each track is stored with a timestamp indicating when it was liked. This enables a unique feature where users can filter their liked songs by date.
- **Playlists**: Users can create playlists and add tracks to them. The relationship between playlists and tracks is managed with a many-to-many association table in the database. Tracks in playlists and liked songs can be retrieved and displayed efficiently.

### **Search Liked Tracks by Date**
One standout feature is the ability to filter liked tracks by the date they were saved. Using SQLAlchemy queries and Flask routes, the app retrieves songs liked on a specific date or date range. This functionality is exposed via both the backend API and the frontend UI.

## Code Highlights

### **Backend API**
1. **Authorization Routes**: OAuth2 token exchanges and Spotify profile syncing are handled in `/callback` and `/authorization`. The app uses Spotify's API endpoints to fetch user information and playlists.
2. **Track Management**: Tracks liked by users are stored with a `date_liked` field, allowing date-based filtering via the `/tracks/date` route.
3. **Database Design**: The schema utilizes relationships for users, tracks, and playlists, ensuring normalized and scalable storage. For example, `playlists_tracks` is a join table linking playlists to tracks.

### **Frontend**
- Dynamic elements (e.g., search results, playlists, and liked tracks) are rendered using **jQuery** and **Axios**. API calls are sent to the backend, and the responses are used to update the DOM in real-time.
- Users can interact with playlists, search results, and liked tracks via modals, forms, and buttons, making the experience intuitive and interactive.

## Lessons Learned
Musify has been an opportunity to practice integrating a third-party API into a full-stack web application while adhering to RESTful principles. Managing session-based user authentication, database relationships, and frontend-backend communication were key takeaways from this project. While there are areas for optimization, the app demonstrates a functional, feature-rich implementation of a music library tool.



![My database image](/static/database-ss-img.png)
