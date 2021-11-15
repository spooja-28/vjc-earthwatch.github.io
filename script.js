function showPlantInformation(plant, info) {
    /*
    plant: ID from 0-...
    info: ID from 0-6 (description, bloom-time, toxicity, cuntry, lifespan, spread)
    */

    for (let i = 0; i <= 6; i++) {
        if (i != info) {
            document.getElementById(`plant-menu-${plant}-${i}`).classList.add("hidden")
        }
    }
    document.getElementById(`plant-menu-${plant}-${info}`).classList.remove("hidden");
}
