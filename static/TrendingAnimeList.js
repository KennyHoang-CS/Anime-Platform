class TrendingAnimeList{

    static async getTrendingAnimes(){
        const response = await axios.get('https://kitsu.io/api/edge/anime');
        // response.data.data[0].attributes.canonicalTitle
        const trendingAnimes = response.data.map(anime => console.log(anime));
    
        return new TrendingAnimeList(trendingAnimes);   
    }

}

let bla = new TrendingAnimeList();



