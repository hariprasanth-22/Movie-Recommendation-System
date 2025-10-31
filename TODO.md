# TODO: Enhance Django Movie Recommender System

## 1. Add New Models (models.py)
- [ ] Add Profile model (per user, with type: adult/kids)
- [ ] Add PreferenceWeights model (per profile, weights for genres/runtime/language/sensitivity)
- [ ] Add WatchEvent model (for Continue Watching, timestamps)
- [ ] Add Feedback model (thumbs up/down, not interested, seen it)
- [ ] Add SavedList model (My List/Watchlist)
- [ ] Add Badge model (gamification)
- [ ] Add Challenge model (weekly challenges)
- [ ] Add Leaderboard model (local leaderboard)
- [ ] Add CachedRecommendations model (precomputed rails per profile)

## 2. Extend utils.py
- [ ] Add load_local_artifacts function
- [ ] Add rank_with_hybrid function (cosine + popularity)
- [ ] Add rerank_for_diversity function (diversity penalty)
- [ ] Add session_rerank function (session-aware re-ranking)
- [ ] Add explain function (badges + confidence)
- [ ] Update MovieRecommender class with new methods

## 3. Create New Views (views.py)
- [ ] Convert to class-based views where needed
- [ ] Add HomeView (hero + rails: Trending, Because you watched X, Continue Watching, For You, My List)
- [ ] Add MovieDetailView (overview, cast, genres, rating; carousels: More like this, Shared cast, Same vibe; feedback; badges)
- [ ] Add SearchView (facets + fuzzy match; saved search chips)
- [ ] Add DashboardView (analytics: favorite genres, completion rate, viewing time; preference sliders; badges; challenges)
- [ ] Add ProfileOnboardingView (genre/title picker + quick-rate wizard)
- [ ] Add AdminCuratorView (pinning, collections, scheduling, A/B toggles)
- [ ] Add POST handlers for feedback, watchlist, quick-rate, preference updates, session events

## 4. Update Templates (templates/recommender/)
- [ ] Update base.html with Netflix-style nav, high-contrast toggle
- [ ] Create components: hero.html, carousel.html, tile.html (with badges + confidence), chips.html, skeletons.html, empty_states.html
- [ ] Update home.html with hero and carousels
- [ ] Update movie_detail.html with carousels and feedback
- [ ] Update search.html with facets and chips
- [ ] Update dashboard.html with analytics and sliders
- [ ] Create onboarding.html
- [ ] Create admin_curator.html

## 5. Update Forms (forms.py)
- [ ] Add forms for onboarding, feedback, preferences, etc.

## 6. Update URLs (urls.py)
- [ ] Add routes for new views and POST endpoints

## 7. Add Management Command
- [ ] Create management/commands/recompute_recs.py for nightly precompute

## 8. Update Settings and Static Files
- [ ] Add caching settings, template dirs, context processors
- [ ] Update CSS for Netflix-style UI (Tailwind or enhanced Bootstrap)
- [ ] Add JS for HTMX partial updates, lazy loading, skeletons

## 9. Run Migrations
- [ ] Create and apply migrations for new models

## 10. Testing
- [ ] Test onboarding flow
- [ ] Test feedback loops and instant rail updates
- [ ] Test cached rails and explainability badges
- [ ] Test kids profile and maturity filters
- [ ] Test gamification and challenges
