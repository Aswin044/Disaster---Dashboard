function initDisasterMap(disaster) {
    console.log(`🌍 Loading map for disaster: ${disaster}`);

    // Initialize the map
    const map = L.map('map').setView([20, 0], 2);

    // Add realistic satellite map layer
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri — Source: Esri, Earthstar Geographics, NASA, USGS, NOAA'
    }).addTo(map);

    // Fetch the data from Flask backend
    fetch(`/api/disaster/${disaster}`)
        .then(res => res.json())
        .then(data => {
            console.log("Fetched disaster data:", data);

            if (!data || data.length === 0) {
                alert("⚠️ No data received from backend!");
                return;
            }

            // Convert data into Leaflet heatmap format
            const heatData = data.map(p => [p.lat, p.lon, p.chance / 100]);
            console.log("Formatted heat data:", heatData);

            // Add the heatmap layer
            L.heatLayer(heatData, {
                radius: 25,
                blur: 15,
                maxZoom: 6,
                gradient: {
                    0.4: 'blue',
                    0.6: 'lime',
                    0.8: 'orange',
                    1.0: 'red'
                }
            }).addTo(map);
        })
        .catch(err => {
            console.error("Error loading map data:", err);
            alert("❌ Could not load map data. Check console for details.");
        });
}
