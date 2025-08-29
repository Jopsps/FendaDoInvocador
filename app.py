from flask import Flask, render_template, request, Response
from ConfigAndApi import get_puuid, get_match_history, get_champions, get_champion_details

app = Flask(__name__)

# Rota principal: histórico de partidas
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        summoner_name = request.form["summonerName"]
        tag_line = request.form.get("tagLine", "BR1")
        game_count = int(request.form.get("gameCount", 5))

        try:
            puuid = get_puuid(summoner_name, tag_line)
            matches = get_match_history(puuid, game_count)

            return render_template(
                "index.html",
                summoner_name=summoner_name,
                tag_line=tag_line,
                matches=matches
            )
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

# Rota de campeões
@app.route("/champions")
def champions():
    try:
        champs = get_champions(locale="pt_BR")
        return render_template("Champions.html", champions=champs)
    except Exception as e:
        return render_template("Champions.html", error=str(e), champions=[])

# Rota de detalhes do campeão
@app.route("/champion/<champ_id>")
def champion_detail(champ_id):
    try:
        champ_data = get_champion_details(champ_id, locale="pt_BR")
        # Adiciona splash principal
        champ_data["splash"] = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_id}_0.jpg"
        return render_template("DetailsChampions.html", champion=champ_data)
    except Exception as e:
        return f"Erro ao carregar o campeão: {str(e)}", 404

@app.route('/riot.txt')
def riot_txt():
    try:
        with open("riot.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()
        return Response(conteudo, mimetype="text/plain")
    except FileNotFoundError:
        return Response("Arquivo riot.txt não encontrado", status=404, mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
