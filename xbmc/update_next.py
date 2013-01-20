import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import json
from collections import defaultdict


class NextUpdatePlayer(xbmc.Player):
    def init(self):
        xbmc.Player.__init__(self)
        self._last_played = None

    def onPlayBackEnded(self):
        self._update_next()

    def onPlayBackStopped(self):
        self._update_next()

    def onPlayBackStarted(self):
        if xbmc.Player().isPlayingVideo():
            players = self._execute_json("Player.GetActivePlayers")
            for p in players:
                if p['type'] == 'video':
                    player_id = p['playerid']
                    break
            if not player_id:
                return
            playing = self._execute_json("Player.GetItem", playerid=player_id)
            type = playing['item']['type']
            id = playing['item']['id']
            if type == 'episode':
                episode = self._execute_json("VideoLibrary.GetEpisodeDetails", episodeid=id,
                                             properties=["showtitle", "season", "episode"])
                self._last_played = episode

    def _update_next(self):
        addon = xbmcaddon.Addon('service.update_next')
        try:
            sys.path.insert(0, os.path.expanduser(addon.getSetting('next_path')))

            import next.db
            import next.util
            import next.constants
        except ImportError:
            xbmcgui.Dialog().ok('next library error!', 'Could not locate next module, have you configured Update Next properly?')
            return

        if not self._last_played:
            return

        if not xbmcgui.Dialog().yesno('Update next?', 'Do you want to update the next database?'):
            return

        episode = self._last_played['episodedetails']
        self._log('Updating next for ' + episode['showtitle'])
        conf = {next.constants.ConfKeys.DB_PATH: addon.getSetting('next_db_path')}
        try:
            next.db.connect(conf)
        except:
            xbmcgui.Dialog().ok('next database error!', 'Could not locate next database, ahve you configured Update Next properly?')
            return

        # Find show
        candidates = next.db.find_shows(conf, episode['showtitle'])
        show = next.util.filter_shows(candidates, episode['showtitle'])

        # Find ep
        eps = next.db.find_all_eps(conf, show.sid, episode['season'])
        for ep in eps:
            if int(episode['episode']) + 1 == ep.epnum:
                next.db.change_show(conf, show.sid, int(episode['season']), int(episode['episode']) + 1)
                break
        else:
            seasons = next.db.find_seasons(conf, show.sid)
            if episode['season'] + 1 in seasons:
                next.db.change_show(conf, show.sid, int(episode['season']) + 1, 1)
            else:
                next.db.change_show(conf, show.sid, int(episode['season']), int(episode['episode']))
                next.db.mark_maybe_finished(conf, show.sid)

        self._last_played = None
        self._log('Done!')

    def _execute_json(self, method, **params):
        cmd = defaultdict(dict,
                          {"jsonrpc": "2.0",
                          "method": method,
                          "id": 1})
        for k, v in params.items():
            cmd["params"][k] = v

        cmd = json.dumps(cmd)
        return json.loads(xbmc.executeJSONRPC(cmd))['result']

    def _log(self, msg):
        xbmc.log('UPDATE_NEXT: ' + str(msg))

player = NextUpdatePlayer()

while(not xbmc.abortRequested):
        xbmc.sleep(100)
