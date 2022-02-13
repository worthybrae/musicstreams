from django.shortcuts import render
from streams.models import Albums, Songs, Songstreams, Albumdist
import datetime
from numerize import numerize
import json
from colorthief import ColorThief
import urllib.request
import numpy as np
from fitter import Fitter, get_common_distributions, get_distributions
import scipy
import pandas as pd
import math
import random
# Create your views here.

def Chartspage(request):
    albums = Albums.objects.filter(status='ACTIVE').order_by('-totalstreams')[:10]
    rank = 1
    r_choice = random.choice([1,2,3,4,5,6,7,8,9,10])
    color_dict = {}
    total_streams_list = []
    streams_per_day_list = []
    daily_growth_list = []
    for album in albums:
        cover = album.cover
        id = album.spotifyid
        name = album.name
        artist = album.artist
        day_0_streams = album.day0streams
        total_streams = album.totalstreams
        total_streams_str = f"{total_streams:,.0f}"
        streams_dict = {}
        for song in album.songs_set.all():
            for songstream in song.songstreams_set.all().order_by('-daterecorded')[:2]:
                if (songstream.daterecorded - album.releasedate).days not in streams_dict:
                    streams_dict[(songstream.daterecorded - album.releasedate).days] = songstream.totalstreams
                else:
                    streams_dict[(songstream.daterecorded - album.releasedate).days] += songstream.totalstreams
        streams_list = []
        for key, value in streams_dict.items():
            streams_list.append([key, value - day_0_streams])
        streams_list.sort(key = lambda x: x[0], reverse = False)
        if streams_list[1][0] == 0:
            streams_per_day = 0
            streams_per_day_str = f"N/A"
        else:
            streams_per_day = streams_list[1][1] / streams_list[1][0]
            streams_per_day_str = f"{streams_per_day:,.0f}"
        if streams_list[0][1] == 0:
            daily_growth = 0
            daily_growth_str = f"N/A"
        else:
            daily_growth = (streams_list[1][1] / streams_list[0][1] - 1) * 100
            daily_growth_str = f"{daily_growth:,.1f}"
        total_streams_list.append([id, cover, name, artist, total_streams, total_streams_str, streams_per_day, streams_per_day_str, daily_growth, daily_growth_str])
        streams_per_day_list.append([id, cover, name, artist, total_streams, total_streams_str, streams_per_day, streams_per_day_str, daily_growth, daily_growth_str])
        daily_growth_list.append([id, cover, name, artist, total_streams, total_streams_str, streams_per_day, streams_per_day_str, daily_growth, daily_growth_str])
        if r_choice == rank:
            urllib.request.urlretrieve(album.cover, "cover.png")
            color_thief = ColorThief('cover.png')
            palette = color_thief.get_palette(color_count=15)
            best_color_match = {'distance': 0}
            for c in palette[:2]:
                for c2 in [x for x in palette if x != c]:
                    color1 = np.asarray(tuple(c))
                    color2 = np.asarray(tuple(c2))
                    rm = 0.5*(color1[0]+color2[0])
                    d = sum((2+rm,4,3-rm)*(color1-color2)**2)**0.5
                    if d > best_color_match['distance']:
                        best_color_match['color1'] = color1
                        best_color_match['color2'] = color2
                        best_color_match['distance'] = d
                        best_color_match['color1gray'] = 0.2126*tuple(c)[0] + 0.7152*tuple(c)[1] + 0.0722*tuple(c)[2]
                        best_color_match['color2gray'] = 0.2126*tuple(c2)[0] + 0.7152*tuple(c2)[1] + 0.0722*tuple(c2)[2]
            if best_color_match['color1gray'] >= 200 and best_color_match['color2gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c2
            elif best_color_match['color2gray'] >= 200 and best_color_match['color1gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c
            elif best_color_match['color1gray'] >= best_color_match['color2gray']:
                best_color_match['colormain'] = c2
                best_color_match['coloralt'] = c
            else:
                best_color_match['colormain'] = c
                best_color_match['coloralt'] = c2
            color_dict['colormainr'] = best_color_match['coloralt'][0] - (255 - best_color_match['coloralt'][0]) * .5
            color_dict['colormaing'] = best_color_match['coloralt'][1] - (255 - best_color_match['coloralt'][1]) * .5
            color_dict['colormainb'] = best_color_match['coloralt'][2] - (255 - best_color_match['coloralt'][2]) * .5
            color_dict['coloraltr'] = best_color_match['colormain'][0] - (255 - best_color_match['colormain'][0]) * .75
            color_dict['coloraltg'] = best_color_match['colormain'][1] - (255 - best_color_match['colormain'][1]) * .75
            color_dict['coloraltb'] = best_color_match['colormain'][2] - (255 - best_color_match['colormain'][2]) * .75
        rank += 1
    total_streams_list.sort(key = lambda x: x[4], reverse = True)
    streams_per_day_list.sort(key = lambda x: x[6], reverse = True)
    daily_growth_list.sort(key = lambda x: x[8], reverse = True)
    return render(request, 'streams/charts.html', {'total_streams_list': total_streams_list, 'streams_per_day_list': streams_per_day_list, 'daily_growth_list': daily_growth_list, 'color_dict': color_dict})


def Detailpage(request, album_spotify_id):
    album = Albums.objects.get(pk=album_spotify_id)
    album_dict = {}
    album_dict['streams_dict'] = {}
    album_dict['name'] = album.name
    album_dict['artist'] = album.artist
    album_dict['releasedate'] = album.releasedate.strftime('%Y')
    album_dict['cover'] = album.cover
    album_dict['runtime'] = 0
    orderlist = []
    playslist = []
    revlist = []
    grolist = []
    album_dict['totalstreams'] = album.totalstreams
    album_dict['totalrevenue'] = album.totalstreams * .00348
    album_dict['totalrevenue'] = f"${album_dict['totalrevenue']:,.0f}"
    if album.totalgrowth == 0:
        album_dict['totalgrowth'] = f"N/A"
    else:
        album_dict['totalgrowth'] = f"{album.totalgrowth:,.0f}%"
    album_dict['maxstreams'] = []
    valence_list = []
    energy_list = []
    danceability_list = []
    songs_order = []
    for song in album.songs_set.all():
        songname = song.name
        songorder = song.songorder
        album_dict['runtime'] += song.duration / 1000
        valence_list.append(song.valence)
        energy_list.append(song.energy)
        danceability_list.append(song.danceability)
        song_streams_list = []
        song_day_0 = song.songstreams_set.all().order_by('daterecorded')[0]
        song_day_0_streams = song_day_0.totalstreams
        for songstream in song.songstreams_set.all().order_by('daterecorded')[1:]:
            song_streams_list.append(songstream.totalstreams - song_day_0_streams)
            if (songstream.daterecorded - album.releasedate).days not in album_dict['streams_dict']:
                album_dict['streams_dict'][(songstream.daterecorded - album.releasedate).days] = songstream.totalstreams - song_day_0_streams
            else:
                album_dict['streams_dict'][(songstream.daterecorded - album.releasedate).days] += songstream.totalstreams - song_day_0_streams


        album_dict['maxstreams'].append(max(song_streams_list))
        songs_order.append([song.name, max(song_streams_list)])
        song_total_revenue_int = max(song_streams_list) * .00348
        song_total_revenue = f"${song_total_revenue_int:,.0f}"
        song_total_streams = f"{max(song_streams_list):,.0f}"
        song_total_streams_int = max(song_streams_list)
        optimized_ss_list = sorted([x for x in song_streams_list if x != 0])
        if len(optimized_ss_list) > 1:
            song_total_growth_int = (optimized_ss_list[len(optimized_ss_list)-1] / optimized_ss_list[0] - 1) * 100
            song_total_growth = f"{song_total_growth_int:,.0f}%"
        else:
            song_total_growth = 'N/A'
            song_total_growth_int = 0
        orderlist.append([songorder, songname, album.artist, song_total_streams, song_total_growth, song_total_revenue, song_total_streams_int, song_total_revenue_int, song_total_growth_int])
        playslist.append([songorder, songname, album.artist, song_total_streams, song_total_growth, song_total_revenue, song_total_streams_int, song_total_revenue_int, song_total_growth_int])
        revlist.append([songorder, songname, album.artist, song_total_streams, song_total_growth, song_total_revenue, song_total_streams_int, song_total_revenue_int, song_total_growth_int])
        grolist.append([songorder, songname, album.artist, song_total_streams, song_total_growth, song_total_revenue, song_total_streams_int, song_total_revenue_int, song_total_growth_int])
    song_growth_list = [x[8] for x in grolist]
    orderlist.sort(key = lambda x: x[0], reverse = False)
    album_dict['orderlist'] = orderlist
    playslist.sort(key = lambda x: x[6], reverse = True)
    album_dict['playslist'] = playslist
    revlist.sort(key = lambda x: x[7], reverse = True)
    album_dict['revlist'] = revlist
    grolist.sort(key = lambda x: x[8], reverse = True)
    album_dict['grolist'] = grolist
    #Sound Calculation
    mean_energy = sum(energy_list) / len(energy_list)
    album_dict['energy'] = round(mean_energy*100)
    if album_dict['energy'] < 5:
        album_dict['energy'] = 0
    mean_valence = sum(valence_list) / len(valence_list)
    album_dict['valence'] = round(mean_valence*100)
    if album_dict['valence'] < 5:
        album_dict['valence'] = 0
    mean_danceability = sum(danceability_list) / len(danceability_list)
    album_dict['danceability'] = round(mean_danceability*100)
    if album_dict['danceability'] < 5:
        album_dict['danceability'] = 0
    streams_list = []
    dsr_list = []
    revenue_list = []
    growth_prep_list = []
    for key, value in album_dict['streams_dict'].items():
        streams_list.append(value)
        dsr_list.append(key)
        revenue_list.append(value * .00348)
        growth_prep_list.append([key, value])
    growth_prep_list.sort(key = lambda x: x[0], reverse = False)
    growth_list = []

    for item in growth_prep_list[1:]:
        if album.day1streams == 0:
            growth_list.append(0)
        else:
            growth_list.append((item[1] / album.day1streams - 1) * 100)

    growth_dsr_list = [x for x in range(2, len(growth_list)+2)]
    album_dict['totalgrowthdata'] = growth_list
    album_dict['totalgrowthlabels'] = growth_dsr_list
    album_dict['totalstreamsdata'] = streams_list
    album_dict['totalrevenuedata'] = revenue_list
    album_dict['totalstreamslabels'] = dsr_list
    current_dsr = max(dsr_list)
    album_dict['dsr'] = current_dsr
    album_dict['totalsongs'] = len(orderlist)
    mean = sum([x for x in album_dict['maxstreams']]) / len([x for x in album_dict['maxstreams']])
    rev_mean = mean * .00348
    gro_mean = sum([x for x in song_growth_list]) / len([x for x in song_growth_list])
    variance = sum([((x - mean) ** 2) for x in [x for x in album_dict['maxstreams']]]) / len([x for x in album_dict['maxstreams']])
    gro_variance = sum([((x - gro_mean) ** 2) for x in [x for x in song_growth_list]]) / len([x for x in song_growth_list])
    if mean == 0:
        res = 0
    else:
        res = ((variance ** 0.5) / mean) * 100
    if gro_mean == 0:
        gro_res = 0
    else:
        gro_res = ((variance ** 0.5) / mean) * 100
    album_dict['covstreams'] = f"{res:,.1f}%"
    album_dict['avgstreams'] = f"{mean:,.0f}"
    album_dict['covgrowth'] = f"{gro_res:,.1f}%"
    album_dict['avggrowth'] = f"{gro_mean:,.0f}%"
    album_dict['avgrevenue'] = f"${rev_mean:,.0f}"
    avg_daily_streams = album_dict['totalstreams'] / album_dict['dsr']
    avg_daily_revenue = avg_daily_streams * .00348
    avg_daily_growth = album.totalgrowth / album_dict['dsr']
    album_dict['avgdailyrevenue'] = f"${avg_daily_revenue:,.0f}"
    album_dict['avgdailystreams'] = f"{avg_daily_streams:,.0f}"
    album_dict['avgdailygrowth'] = f"{avg_daily_growth:,.0f}%"
    album_dict['totalstreams'] = f"{album_dict['totalstreams']:,.0f}"

    dist_streams = []
    for album_dist in Albumdist.objects.filter(dsr=current_dsr):
        dist_streams.append(album_dist.totalstreams)
    dist_min = min(dist_streams)
    dist_max = max(dist_streams)
    df = pd.DataFrame({'streams': dist_streams})
    s = df['streams'].values
    f = Fitter(s, distributions = ['expon',])
    f.fit()
    results = f.get_best(method = 'sumsquare_error')
    rv = scipy.stats.expon(loc=results['expon']['loc'], scale=results['expon']['scale'])
    streams = []
    fillprobs = []
    nofillprobs = []
    probs = []
    cond_streams = np.linspace(dist_min, dist_max, 5000)
    album_dict['totalstreamsint'] = album.totalstreams
    for i in cond_streams:
        streams.append(i)
        if i <= album_dict['totalstreamsint']:
            p = rv.cdf(i) * 100
            fillprobs.append(p)
            probs.append(p)
        else:
            p = rv.cdf(i) * 100
            nofillprobs.append(p)
            probs.append(p)
    album_dict['totalstreamsint'] = album.totalstreams
    streams.append(album.totalstreams)
    streams.sort()
    fillprobs.append(rv.cdf(album.totalstreams) * 100)
    fillprobs.sort()
    probs.append(rv.cdf(album.totalstreams) * 100)
    probs.sort()
    album_dict['streamsbysongdatafill'] = fillprobs
    album_dict['streamsbysonglabels'] = streams
    album_dict['streamsbysongdatanofill'] = nofillprobs
    album_dict['streamsbysongdata'] = probs
    #Percentile Label Formatting
    xcdf = rv.cdf(album.totalstreams) * 100
    album_dict['totalstreamspercentile'] = f"{round(rv.cdf(album.totalstreams) * 100, 0):.0f}"
    album_dict['percentiledecimal'] = rv.cdf(album.totalstreams) * 100
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    album_dict['percentilelabel'] = ordinal(int(round(album_dict['percentiledecimal'], 0)))
    if 91 <= round(xcdf, 0) <= 100:
        album_dict['toplabel'] = xcdf
        album_dict['upplabel'] = 80
        album_dict['uppmidlabel'] = 60
        album_dict['lowmidlabel'] = 40
        album_dict['lowlabel'] = 20
        album_dict['bottomlabel'] = 1
        album_dict['toplabelval'] = rv.ppf(xcdf/100)
        album_dict['upplabelval'] = rv.ppf(.80)
        album_dict['uppmidlabelval'] = rv.ppf(.60)
        album_dict['lowmidlabelval'] = rv.ppf(.40)
        album_dict['lowlabelval'] = rv.ppf(.20)
        album_dict['bottomlabelval'] = rv.ppf(.01)
    elif 71 <= round(xcdf, 0) <= 90:
        album_dict['toplabel'] = 99.9
        album_dict['upplabel'] = xcdf
        album_dict['uppmidlabel'] = 60
        album_dict['lowmidlabel'] = 40
        album_dict['lowlabel'] = 20
        album_dict['bottomlabel'] = 1
        album_dict['toplabelval'] = rv.ppf(.999)
        album_dict['upplabelval'] = rv.ppf(xcdf/100)
        album_dict['uppmidlabelval'] = rv.ppf(.60)
        album_dict['lowmidlabelval'] = rv.ppf(.40)
        album_dict['lowlabelval'] = rv.ppf(.20)
        album_dict['bottomlabelval'] = rv.ppf(.01)
    elif 51 <= round(xcdf, 0) <= 70:
        album_dict['toplabel'] = 99.9
        album_dict['upplabel'] = 80
        album_dict['uppmidlabel'] = xcdf
        album_dict['lowmidlabel'] = 40
        album_dict['lowlabel'] = 20
        album_dict['bottomlabel'] = 1
        album_dict['toplabelval'] = rv.ppf(.999)
        album_dict['upplabelval'] = rv.ppf(.8)
        album_dict['uppmidlabelval'] = rv.ppf(xcdf/100)
        album_dict['lowmidlabelval'] = rv.ppf(.40)
        album_dict['lowlabelval'] = rv.ppf(.20)
        album_dict['bottomlabelval'] = rv.ppf(.01)
    elif 31 <= round(xcdf, 0) <= 50:
        album_dict['toplabel'] = 99.9
        album_dict['upplabel'] = 80
        album_dict['uppmidlabel'] = 60
        album_dict['lowmidlabel'] = xcdf
        album_dict['lowlabel'] = 20
        album_dict['bottomlabel'] = 1
        album_dict['toplabelval'] = rv.ppf(.999)
        album_dict['upplabelval'] = rv.ppf(.80)
        album_dict['uppmidlabelval'] = rv.ppf(.60)
        album_dict['lowmidlabelval'] = rv.ppf(xcdf/100)
        album_dict['lowlabelval'] = rv.ppf(.20)
        album_dict['bottomlabelval'] = rv.ppf(.01)
    elif 11 <= round(xcdf, 0) <= 30:
        album_dict['toplabel'] = 99.9
        album_dict['upplabel'] = 80
        album_dict['uppmidlabel'] = 60
        album_dict['lowmidlabel'] = 40
        album_dict['lowlabel'] = xcdf
        album_dict['bottomlabel'] = 1
        album_dict['toplabelval'] = rv.ppf(.999)
        album_dict['upplabelval'] = rv.ppf(.80)
        album_dict['uppmidlabelval'] = rv.ppf(.60)
        album_dict['lowmidlabelval'] = rv.ppf(.40)
        album_dict['lowlabelval'] = rv.ppf(xcdf/100)
        album_dict['bottomlabelval'] = rv.ppf(.01)
    else:
        album_dict['toplabel'] = 99.9
        album_dict['upplabel'] = 80
        album_dict['uppmidlabel'] = 60
        album_dict['lowmidlabel'] = 40
        album_dict['lowlabel'] = 20
        album_dict['bottomlabel'] = xcdf
        album_dict['toplabelval'] = rv.ppf(.999)
        album_dict['upplabelval'] = rv.ppf(.80)
        album_dict['uppmidlabelval'] = rv.ppf(.60)
        album_dict['lowmidlabelval'] = rv.ppf(.40)
        album_dict['lowlabelval'] = rv.ppf(.2)
        album_dict['bottomlabelval'] = rv.ppf(xcdf/100)
    #Runtime String Formatting
    album_dict['runtime'] = str(datetime.timedelta(seconds=album_dict['runtime'])).split(':')
    if int(album_dict['runtime'][0]) != 0:
        total_hours = int(album_dict['runtime'][0])
        total_minutes = int(album_dict['runtime'][1])
        if total_minutes != 0:
            album_dict['runtime'] = f'{total_hours:.0f} hr {total_minutes:.0f} min'
        else:
            album_dict['runtime'] = f'{total_hours:.0f} hr'
    else:
        total_minutes = int(album_dict['runtime'][1])
        total_seconds = float(album_dict['runtime'][2])
        if total_seconds != 0:
            album_dict['runtime'] = f'{total_minutes:.0f} min {total_seconds:.0f} sec'
        else:
            album_dict['runtime'] = f'{total_minutes:.0f} min'
    #Color Render
    urllib.request.urlretrieve(album.cover, "cover.png")
    color_thief = ColorThief('cover.png')
    palette = color_thief.get_palette(color_count=15)
    best_color_match = {'distance': 0}
    for c in palette[:2]:
        for c2 in [x for x in palette if x != c]:
            color1 = np.asarray(tuple(c))
            color2 = np.asarray(tuple(c2))
            rm = 0.5*(color1[0]+color2[0])
            d = sum((2+rm,4,3-rm)*(color1-color2)**2)**0.5
            if d > best_color_match['distance']:
                best_color_match['color1'] = color1
                best_color_match['color2'] = color2
                best_color_match['distance'] = d
                best_color_match['color1gray'] = 0.2126*tuple(c)[0] + 0.7152*tuple(c)[1] + 0.0722*tuple(c)[2]
                best_color_match['color2gray'] = 0.2126*tuple(c2)[0] + 0.7152*tuple(c2)[1] + 0.0722*tuple(c2)[2]
    if best_color_match['distance'] == 0:
        best_color_match['coloralt'] = color1
        best_color_match['colormain'] = (90, 90, 90)
    else:
        if best_color_match['color1gray'] >= 200 and best_color_match['color2gray'] > 127:
            best_color_match['colormain'] = (90,90,90)
            best_color_match['coloralt'] = c2
        elif best_color_match['color2gray'] >= 200 and best_color_match['color1gray'] > 127:
            best_color_match['colormain'] = (90,90,90)
            best_color_match['coloralt'] = c
        elif best_color_match['color1gray'] >= best_color_match['color2gray']:
            best_color_match['colormain'] = c2
            best_color_match['coloralt'] = c
        else:
            best_color_match['colormain'] = c
            best_color_match['coloralt'] = c2
    album_dict['colormainr'] = best_color_match['coloralt'][0] - (255 - best_color_match['coloralt'][0]) * .5
    album_dict['colormaing'] = best_color_match['coloralt'][1] - (255 - best_color_match['coloralt'][1]) * .5
    album_dict['colormainb'] = best_color_match['coloralt'][2] - (255 - best_color_match['coloralt'][2]) * .5
    album_dict['coloraltr'] = best_color_match['colormain'][0] - (255 - best_color_match['colormain'][0]) * .75
    album_dict['coloraltg'] = best_color_match['colormain'][1] - (255 - best_color_match['colormain'][1]) * .75
    album_dict['coloraltb'] = best_color_match['colormain'][2] - (255 - best_color_match['colormain'][2]) * .75
    return render(request, 'streams/detail.html', {'album_dict': album_dict})


def Homepage(request):
    all_albums = Albums.objects.filter(day1streams__gt=0).order_by('-totalstreams')
    top_growth = []
    albums = Albums.objects.filter(status='ACTIVE').order_by('-totalgrowth')[:5]
    rank = 1
    r_choice = random.choice([1,2,3,4,5])
    color_dict = {}
    for album in albums:
        album_spotify_id = album.spotifyid
        album_name = album.name
        artist_name = album.artist
        cover_art = album.cover
        day_0_streams = album.day0streams
        streams_dict = {}
        for song in album.songs_set.all():
            for songstream in song.songstreams_set.all():
                if songstream.daterecorded not in streams_dict:
                    streams_dict[songstream.daterecorded] = songstream.totalstreams
                else:
                    streams_dict[songstream.daterecorded] += songstream.totalstreams
        streams_list = []

        dates_list = []
        for k, v in streams_dict.items():
            dates_list.append(k)
            streams_list.append(v - day_0_streams)
        streams_list = sorted(streams_list)[1:]
        dsr_list = list(range(1, len(dates_list[1:])+1))
        total_streams = numerize.numerize(album.totalstreams, 0)
        top_growth.append([rank, album_spotify_id, album_name, artist_name, cover_art, streams_list, dsr_list, total_streams])
        if r_choice == rank:
            urllib.request.urlretrieve(album.cover, "cover.png")
            color_thief = ColorThief('cover.png')
            palette = color_thief.get_palette(color_count=15)
            best_color_match = {'distance': 0}
            for c in palette[:2]:
                for c2 in [x for x in palette if x != c]:
                    color1 = np.asarray(tuple(c))
                    color2 = np.asarray(tuple(c2))
                    rm = 0.5*(color1[0]+color2[0])
                    d = sum((2+rm,4,3-rm)*(color1-color2)**2)**0.5
                    if d > best_color_match['distance']:
                        best_color_match['color1'] = color1
                        best_color_match['color2'] = color2
                        best_color_match['distance'] = d
                        best_color_match['color1gray'] = 0.2126*tuple(c)[0] + 0.7152*tuple(c)[1] + 0.0722*tuple(c)[2]
                        best_color_match['color2gray'] = 0.2126*tuple(c2)[0] + 0.7152*tuple(c2)[1] + 0.0722*tuple(c2)[2]
            if best_color_match['color1gray'] >= 200 and best_color_match['color2gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c2
            elif best_color_match['color2gray'] >= 200 and best_color_match['color1gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c
            elif best_color_match['color1gray'] >= best_color_match['color2gray']:
                best_color_match['colormain'] = c2
                best_color_match['coloralt'] = c
            else:
                best_color_match['colormain'] = c
                best_color_match['coloralt'] = c2
            color_dict['colormainr'] = best_color_match['coloralt'][0] - (255 - best_color_match['coloralt'][0]) * .5
            color_dict['colormaing'] = best_color_match['coloralt'][1] - (255 - best_color_match['coloralt'][1]) * .5
            color_dict['colormainb'] = best_color_match['coloralt'][2] - (255 - best_color_match['coloralt'][2]) * .5
            color_dict['coloraltr'] = best_color_match['colormain'][0] - (255 - best_color_match['colormain'][0]) * .75
            color_dict['coloraltg'] = best_color_match['colormain'][1] - (255 - best_color_match['colormain'][1]) * .75
            color_dict['coloraltb'] = best_color_match['colormain'][2] - (255 - best_color_match['colormain'][2]) * .75
        rank += 1
    return render(request, 'streams/home.html', {'top_growth': top_growth, 'all_albums': all_albums, 'color_dict': color_dict})

def Performancepage(request):
    performance_dict = {}
    all_albums = Albums.objects.all().order_by('releasedate')
    performance_dict['totalalbums'] = numerize.numerize(len(all_albums), 0)
    all_songs = Songs.objects.all()
    performance_dict['totalsongs'] = numerize.numerize(len(all_songs), 0)
    all_songstreams = Songstreams.objects.all()
    performance_dict['totalsongstreams'] = numerize.numerize(len(all_songstreams), 0)
    release_data = {}
    points_data = {}
    for album in all_albums:
        if (datetime.date.today() - album.releasedate).days not in release_data:
            release_data[(datetime.date.today() - album.releasedate).days] = 1
        else:
            release_data[(datetime.date.today() - album.releasedate).days] += 1
    for songstream in all_songstreams:
        if (datetime.date.today() - songstream.daterecorded).days not in points_data:
            points_data[(datetime.date.today() -  songstream.daterecorded).days] = 1
        else:
            points_data[(datetime.date.today() -  songstream.daterecorded).days] += 1
    performance_dict['releasedata'] = []
    performance_dict['releaselabels'] = []
    old_value = 0
    for key, value in release_data.items():
        performance_dict['releasedata'].append(value + old_value)
        performance_dict['releaselabels'].append(key)
        old_value = value + old_value

    performance_dict['pointsdata'] = []
    performance_dict['pointslabels'] = []

    old_value = 0
    for key, value in points_data.items():
        performance_dict['pointsdata'].append(value + old_value)
        performance_dict['pointslabels'].append(key)
        old_value = value + old_value
    performance_dict['pointsdata'].sort()
    performance_dict['pointslabels'].sort()
    performance_dict['dayscollected'] = max(performance_dict['pointslabels'])
    albums = Albums.objects.filter(status='ACTIVE').order_by('-totalgrowth')[:5]
    rank = 1
    r_choice = random.choice([1,2,3,4,5])
    color_dict = {}
    for album in albums:
        if r_choice == rank:
            urllib.request.urlretrieve(album.cover, "cover.png")
            color_thief = ColorThief('cover.png')
            palette = color_thief.get_palette(color_count=15)
            best_color_match = {'distance': 0}
            for c in palette[:2]:
                for c2 in [x for x in palette if x != c]:
                    color1 = np.asarray(tuple(c))
                    color2 = np.asarray(tuple(c2))
                    rm = 0.5*(color1[0]+color2[0])
                    d = sum((2+rm,4,3-rm)*(color1-color2)**2)**0.5
                    if d > best_color_match['distance']:
                        best_color_match['color1'] = color1
                        best_color_match['color2'] = color2
                        best_color_match['distance'] = d
                        best_color_match['color1gray'] = 0.2126*tuple(c)[0] + 0.7152*tuple(c)[1] + 0.0722*tuple(c)[2]
                        best_color_match['color2gray'] = 0.2126*tuple(c2)[0] + 0.7152*tuple(c2)[1] + 0.0722*tuple(c2)[2]
            if best_color_match['color1gray'] >= 200 and best_color_match['color2gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c2
            elif best_color_match['color2gray'] >= 200 and best_color_match['color1gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c
            elif best_color_match['color1gray'] >= best_color_match['color2gray']:
                best_color_match['colormain'] = c2
                best_color_match['coloralt'] = c
            else:
                best_color_match['colormain'] = c
                best_color_match['coloralt'] = c2
            color_dict['colormainr'] = best_color_match['coloralt'][0] - (255 - best_color_match['coloralt'][0]) * .5
            color_dict['colormaing'] = best_color_match['coloralt'][1] - (255 - best_color_match['coloralt'][1]) * .5
            color_dict['colormainb'] = best_color_match['coloralt'][2] - (255 - best_color_match['coloralt'][2]) * .5
            color_dict['coloraltr'] = best_color_match['colormain'][0] - (255 - best_color_match['colormain'][0]) * .75
            color_dict['coloraltg'] = best_color_match['colormain'][1] - (255 - best_color_match['colormain'][1]) * .75
            color_dict['coloraltb'] = best_color_match['colormain'][2] - (255 - best_color_match['colormain'][2]) * .75
        rank += 1
    return render(request, 'streams/performance.html', {'performance_dict': performance_dict, 'color_dict': color_dict})

def Aboutpage(request):
    albums = Albums.objects.filter(status='ACTIVE').order_by('-totalgrowth')[:5]
    rank = 1
    r_choice = random.choice([1,2,3,4,5])
    color_dict = {}
    for album in albums:
        if r_choice == rank:
            urllib.request.urlretrieve(album.cover, "cover.png")
            color_thief = ColorThief('cover.png')
            palette = color_thief.get_palette(color_count=15)
            best_color_match = {'distance': 0}
            for c in palette[:2]:
                for c2 in [x for x in palette if x != c]:
                    color1 = np.asarray(tuple(c))
                    color2 = np.asarray(tuple(c2))
                    rm = 0.5*(color1[0]+color2[0])
                    d = sum((2+rm,4,3-rm)*(color1-color2)**2)**0.5
                    if d > best_color_match['distance']:
                        best_color_match['color1'] = color1
                        best_color_match['color2'] = color2
                        best_color_match['distance'] = d
                        best_color_match['color1gray'] = 0.2126*tuple(c)[0] + 0.7152*tuple(c)[1] + 0.0722*tuple(c)[2]
                        best_color_match['color2gray'] = 0.2126*tuple(c2)[0] + 0.7152*tuple(c2)[1] + 0.0722*tuple(c2)[2]
            if best_color_match['color1gray'] >= 200 and best_color_match['color2gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c2
            elif best_color_match['color2gray'] >= 200 and best_color_match['color1gray'] > 127:
                best_color_match['colormain'] = (90,90,90)
                best_color_match['coloralt'] = c
            elif best_color_match['color1gray'] >= best_color_match['color2gray']:
                best_color_match['colormain'] = c2
                best_color_match['coloralt'] = c
            else:
                best_color_match['colormain'] = c
                best_color_match['coloralt'] = c2
            color_dict['colormainr'] = best_color_match['coloralt'][0] - (255 - best_color_match['coloralt'][0]) * .5
            color_dict['colormaing'] = best_color_match['coloralt'][1] - (255 - best_color_match['coloralt'][1]) * .5
            color_dict['colormainb'] = best_color_match['coloralt'][2] - (255 - best_color_match['coloralt'][2]) * .5
            color_dict['coloraltr'] = best_color_match['colormain'][0] - (255 - best_color_match['colormain'][0]) * .75
            color_dict['coloraltg'] = best_color_match['colormain'][1] - (255 - best_color_match['colormain'][1]) * .75
            color_dict['coloraltb'] = best_color_match['colormain'][2] - (255 - best_color_match['colormain'][2]) * .75
        rank += 1
    return render(request, 'streams/about.html', {'color_dict': color_dict})
