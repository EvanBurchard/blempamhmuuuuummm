const { SlippiGame } = require("@slippi/slippi-js");
const fs = require("fs");

if (process.argv[2]){
    game_name = process.argv[2]
} else {
    game_name = "test_game.slp"
}

const analytics_directory = "./game_analytics"
const game = new SlippiGame(game_name);
game_stats = {game_name: game_name, 
                settings: game.getSettings(),
                metadata: game.getMetadata(),
                stats: game.getStats(),
                // frames: game.getFrames() 
                // Frames makes the output files way bigger (14 mb analytics file on a 2 mb game file)
                // Analytics file is only 22 kb without it
             }

if (!fs.existsSync(analytics_directory)) {
    fs.mkdirSync(analytics_directory, 0744);
}
// extract just file name

fs.writeFile(analytics_directory + "/" + game_name.split('/').pop().replace('.slp', '.json'), JSON.stringify(game_stats), (error) => {
    if (error) throw error;
});
