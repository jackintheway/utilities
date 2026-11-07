#!/bin/bash
# Build Local Reviewer.app (a drag-and-drop droplet) next to this script from local-review-app.applescript.
set -e
cd "$(dirname "$0")"
rm -rf "Local Reviewer.app"
osacompile -o "Local Reviewer.app" local-review-app.applescript
# Accept video files dropped on it.
plist="Local Reviewer.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Delete :CFBundleDocumentTypes" "$plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :CFBundleDocumentTypes array" \
  -c "Add :CFBundleDocumentTypes:0 dict" \
  -c "Add :CFBundleDocumentTypes:0:CFBundleTypeRole string Viewer" \
  -c "Add :CFBundleDocumentTypes:0:LSItemContentTypes array" \
  -c "Add :CFBundleDocumentTypes:0:LSItemContentTypes:0 string public.movie" \
  -c "Add :CFBundleIdentifier string local.review.droplet" "$plist" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier local.review.droplet" "$plist"
codesign --force --deep -s - "Local Reviewer.app"   # re-sign after the plist edit (local, ad hoc)
echo "Built $(pwd)/Local Reviewer.app"
