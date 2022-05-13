# A simple script of igv.js for visulization of BAM, BigWig and etc.

import sys
import argparse
import json
import wget
import os
import re
from os.path import basename
from os.path import isfile
try:
    # For Python3
    import http.server as SimpleHTTPServer
except ImportError:
    # For Python2
    import SimpleHTTPServer


def get_opt():
    # get all arguments
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-r", "--ref", help="load own reference fasta file", required=False)
    arguments.add_argument("-rn","--reference", help="enter the reference name, load reference from internet, \
        you can choose one ref from genome.json provided by -gl", required=False)
    arguments.add_argument("-m", "--bam", help="Input mapping file, in1.bam in2.bam ... Besides, \
        only bam files are needed when input arguments, and index files(.bai) should be saved in the \
        same directory and named as same basename with bam files", required=False, nargs = "*")
    arguments.add_argument("-w", "--bigwig", help="Input bigwig file, in1.bw in2.bw ...", required=False, nargs = "*")
    arguments.add_argument("-b", "--bed", help="bed annotation", required=False)
    arguments.add_argument("-g", "--gtf", help="gtf annotation", required=False, nargs = "*")
    arguments.add_argument("-l", "--locus", help="Name of gene or the locus of gene, IGV will automatically \
        locate to the target location. this function may not support your own reference genome", required=False,
        default='')
    arguments.add_argument("-gl", "--genomelist", help="list the reference genomes supported online and \
        save the genomes.json file", action="store_true",required=False)
    arguments.add_argument("-p","--port", default=8890, type=int, required=False, help='Specify alternate \
        port [default: 8890]')
    arguments.add_argument("-ab","--addbam", help="Add Bam files when index.html exists.",required=False)
    arguments.add_argument("-rb","--rmbam", help="remove the bam based on bam_id", required=False)
    arguments.add_argument("-roi","--ROI", help="Regions of interest, the value of an ROI is an annotation track \
        configuration object, so please input a file.", required=False)

    return arguments.parse_args()
    # get the terminal arguements behind the command

def build_bam_tracks(bams):
    tracks = []

    for bam in bams:
        if not isfile( bam + ".bai"):
            print("{}.bai is not existed".format(bam), file=sys.stderr)
            sys.exit()
        bam_id = basename(bam).replace(".bam","")

        # track = """
        # {{
        #     "name": "{bam_id}",
        #     "type": "alignment",
        #     "format": "bam",
        #     "url": "{bam}",
        #     "indexURL": "{bam}.bai"
        # }}""".format(bam = bam, bam_id = bam_id)

        track = {
            "name": "",
            "type": "alignment",
            "format": "bam",
            "url": "",
            "indexURL": "",
        }
        track["name"] = bam_id
        track["url"] = bam
        track["indexURL"] = bam+".bai"
        
        # track: dict -> json and save in the Cache
        track = json.dumps(track, sort_keys=True, indent=4, separators=(',',': '))
        file = 'Cache/'+bam_id+'.json'
        with open(file,'w') as file_obj:
            json.dump(track,file_obj)

    #     tracks.append(track)
    # tracks = "".join(tracks)[:-1]
    # return tracks

def build_bw_tracks(bigwigs):
    tracks = []
    for bigwig in bigwigs:
        bw_id = basename(bigwig).replace(".bw","").replace(".bigwig","").replace(".bigWig","").replace("BigWig","")
        
        # track = """
        # {{
        #     name: "{bw_id}",
        #     format: "bigwig",
        #     url: "{bigwig}"
        # }},""".format(bw_id = bw_id, bigwig = bigwig)

        track = {
            "name": "",
            "format": "bigwig",
            "url": "",
        }
        track["name"] = bw_id
        track["url"] = bigwig

        track = json.dumps(track, sort_keys=True, indent=4, separators=(',',': '))
        file = 'Cache/'+bw_id+'.json'
        with open(file,'w') as file_obj:
            json.dump(track,file_obj)

    #     tracks.append(track)
    # tracks = "".join(tracks)[:-1]
    # return tracks

def build_gtf_tracks(gtfs):
    tracks =  [] 
    for gtf in gtfs:

    #     track = """
	# {{
	#     type: "annotation",
    #         format: "gtf",
    #         sourceType: "file",
    #         url: "{gtf}",
    #         visibilityWindow: 500000,
    #         displayMode: "COLLAPSED",
    #         autoHeight: true
	# }},""".format(gtf = gtf)

        track = {
            "type": "annotation",
            "format": "gtf",
            "url": "",
            "visibilityWindow": 500000,
            "displayMode": "COLLAPSED",
            "autoHeight": "true",
        }
        track["url"] = gtf

        track = json.dumps(track, sort_keys=True, indent=4, separators=(',',': '))
        file = 'Cache/'+gtf+'.json'
        with open(file,'w') as file_obj:
            json.dump(track,file_obj)

    #     tracks.append(track)
    # tracks = "".join(tracks)[:-1]	
    # return tracks

def build_bed_tracks(bed):

    # track = """
	# {{
	#     type: "annotation",
    #         format: "bed",
    #         sourceType: "file",
    #         url: "{bed}",
    #         order: Number.MAX_VALUE,
    #         visibilityWindow: 300000000,
    #         displayMode: "EXPANDED"
	# }}
	# """.format(bed = bed)

    track = {
        "type": "annotation",
        "format": "bed",
        "sourceType": "file",
        "url": "",
        "visibilityWindow": 300000000,
        "displayMode": "EXPANDED",
    }
    track["url"] = bed

    track = json.dumps(track, sort_keys=True, indent=4, separators=(',',': '))
    file = 'Cache/'+bed+'.json'
    with open(file,'w') as file_obj:
        json.dump(track,file_obj)

def build_ref_track(fasta):
    # build the local reference genome 
    if not isfile( fasta + ".fai"):
        print("{}.fai is not existed".format(fasta), file=sys.stderr)
        sys.exit()

    genome = basename(fasta)
    genome_id = genome.replace(".fasta","").replace(".fas","").replace(".fa","")

    ref_track ="{{ id: \"{genome_id}\",fastaURL: \"{fasta}\", indexURL: \"{fasta}.fai\"}}".format(genome_id = genome_id, fasta = fasta)
    return ref_track

def build_refn_track(refn):
    # build the reference genome from online source
    bam_track ="""genome: "{genome}" """.format(genome = refn)
    return bam_track


def make_html(genome, tracks, locus, roi):
    # make html file which will be opened as a website.
    html="""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>igv.js</title>
        <script src="igv.js"></script>

    </head>

    <body>
        <div id="igv-div"></div>
    </body>
    <script>

    function getUrlParam(name) {
        //构造一个含有目标参数的正则表达式对象
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        //匹配目标参数
        var r = window.location.search.substr(1).match(reg);
        //返回参数值
        if(r != null) {
            return decodeURI(r[2]);
        }
        return null;
    }
    var print = console.log
        window.onload=function(){
            //console.log(getUrlParam("chr"))
            var chr = getUrlParam("chr")
            print(chr)
            if (chr === null){
                chr = "{locus}";
            }
            var aColors = getUrlParam("colors")
            if (aColors === null){
                aColors = "{color}";
            }
            print(aColors)
            var ref = getUrlParam("genome");
            var refer = {genome}
            if (ref === null){
                ref = "";
            }else{
                refer = "";
            }

        var igvDiv = document.getElementById("igv-div");

        var options = {
            showNavigation: true,
            showRuler: true,
            genome: ref ,
            reference: refer,
            locus: chr,
            roi:[{
                    name: 'ROI set',
                    url: '{roi}',
                    indexed: false,
                    color: "rgba(68, 134, 247, 0.25)"
            }] ,
            tracks: [
                {tracks}
            ]
        };
            
        igv.createBrowser(igvDiv, options)
            .then(function (browser) {
                console.log("Created IGV browser");
                }   
            )   
        }
    </script>
    </html>""".format(tracks = tracks,genome = genome,locus = locus, roi = roi)

    return html

def write_html(html):
    # write whole content into html file.
    with open("index.html", "w") as file:
        file.writelines(html)

def igv_web(fasta, bams, bws, bed, gtfs, locus, refn, roi):
    # to check whether files exist and build the content of html.
    if bams is None and bws is None and bed is None and gtfs is None:
        return

    tracks = ""
    if fasta is not None:
        genome_track = build_ref_track(fasta)
    else:
        genome_track = ""
    if refn is not None:
        genome_track = build_refn_track(refn)
    if bams is not None:
        build_bam_tracks(bams)
    if bws is not None:
        build_bw_tracks(bws)
    if gtfs is not None:
        build_gtf_tracks(gtfs)
    if bed is not None:
        build_bed_tracks(bed)


    filelist = os.listdir(path="Cache/")
    for item in filelist:
        file = open("Cache/"+item,'r')
        content = json.load(file)
        tracks = tracks + content + ','
    tracks = tracks[:-1]
    if roi is None:
        roi = "https://s3.amazonaws.com/igv.org.test/data/roi/roi_bed_1.bed"
    html = make_html( genome_track, tracks, locus, roi)

    write_html(html)

def print_genomelist():
    # print genomelist supported online
    if not isfile('genomes.json'):
        url = 'https://s3.amazonaws.com/igv.org.genomes/genomes.json'
        path = './genomes.json'
        wget.download(url,path)
    file = open('genomes.json')
    data = json.load(file)
    print('The following reference genomes have been supported:')
    for i in range(0,len(data)):
        print(data[i]["id"])

def create_cache():
    isExist = os.path.exists('Cache')
    if not isExist:
        os.makedirs("Cache")
        return True
    else:
        return False

def add_bam(addbam):
    #add bam files into index.html
    if addbam is None:
        return
    build_bam_tracks([addbam])

    f = open('index.html','r',encoding='utf-8')
    html = f.read()
    f.close
    con = html.split('[')
    before = con[0] + '['

    # before = re.findall(r'.(.*?)tracks:', html, re.S)
    # mid = re.findall(r'tracks: \[(.*?)\]', html, re.S)

    con = html.split(']')
    last = ']'+con[1]

    tracks = ''
    # read all files in Cache folder
    filelist = os.listdir(path="Cache/")
    for item in filelist:
        file = open("Cache/"+item,'r')
        content = json.load(file)
        tracks = tracks + content + ','
    tracks = tracks[:-1]
    content = before + tracks + last
    file = open('index.html','w')
    file.write(content)
    file.close

def remove_bam(rmbam):
    #remove bam files from index.html
    if rmbam is None:
        return
    rmbam_id = basename(rmbam).replace(".bam","")
    os.remove("Cache/"+rmbam_id+".json")
    f = open('index.html','r',encoding='utf-8')
    html = f.read()
    f.close
    con = html.split('[')
    before = con[0] + '['

    # before = re.findall(r'.(.*?)tracks:', html, re.S)
    # mid = re.findall(r'tracks: \[(.*?)\]', html, re.S)

    con = html.split(']')
    last = ']'+con[1]

    tracks = ''
    # read all files in Cache folder
    filelist = os.listdir(path="Cache/")
    for item in filelist:
        file = open("Cache/"+item,'r')
        content = json.load(file)
        tracks = tracks + content + ','
    tracks = tracks[:-1]
    content = before + tracks + last
    file = open('index.html','w')
    file.write(content)
    file.close


def create_server(port):
    # create python server which supported rangerequest.
    SimpleHTTPServer.test(HandlerClass=RangeRequestHandler, port=port)

def copy_byte_range(infile, outfile, start=None, stop=None, bufsize=16*1024):
    '''Like shutil.copyfileobj, but only copy a range of the streams.

    Both start and stop are inclusive.
    '''
    if start is not None: infile.seek(start)
    while 1:
        to_read = min(bufsize, stop + 1 - infile.tell() if stop else bufsize)
        # In this cycle, file to read will be divided into many subfile (which length is bufsize).
        # and those subfiles will be writed into outfile
        buf = infile.read(to_read)
        if not buf:
            break
        outfile.write(buf)

BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')

def parse_byte_range(byte_range):
    '''Returns the two numbers in 'bytes=123-456' or throws ValueError.

    The last number or both numbers may be None.
    '''
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range %s' % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError('Invalid byte range %s' % byte_range)
    return first, last

class RangeRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Adds support for HTTP 'Range' requests to SimpleHTTPRequestHandler

    The approach is to:
    - Override send_head to look for 'Range' and respond appropriately.
    - Override copyfile to only transmit a range when requested.
    """
    def send_head(self):
        if 'Range' not in self.headers:
            self.range = None
            return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)
        try:
            self.range = parse_byte_range(self.headers['Range'])
        except ValueError as e:
            self.send_error(400, 'Invalid byte range')
            return None
        first, last = self.range

        # Mirroring SimpleHTTPServer.py here
        path = self.translate_path(self.path)
        f = None
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, 'File not found')
            return None

        fs = os.fstat(f.fileno())
        file_len = fs[6]
        if first >= file_len:
            self.send_error(416, 'Requested Range Not Satisfiable')
            return None

        self.send_response(206)
        self.send_header('Content-type', ctype)
        self.send_header('Accept-Ranges', 'bytes')

        if last is None or last >= file_len:
            last = file_len - 1
        response_length = last - first + 1

        self.send_header('Content-Range',
                         'bytes %s-%s/%s' % (first, last, file_len))
        self.send_header('Content-Length', str(response_length))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        if not self.range:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.copyfile(self, source, outputfile)

        # SimpleHTTPRequestHandler uses shutil.copyfileobj, which doesn't let
        # you stop the copying before the end of the file.
        start, stop = self.range  # set in send_head()
        copy_byte_range(source, outputfile, start, stop)


if __name__ == "__main__":
    create_cache()
    opts = get_opt()
    if opts.genomelist is False:
        bams = opts.bam
        fasta = opts.ref
        refn = opts.reference
        bed = opts.bed
        gtfs = opts.gtf
        bws = opts.bigwig
        locus = opts.locus
        port = opts.port
        addbam = opts.addbam
        rmbam = opts.rmbam
        roi = opts.ROI
        igv_web(fasta, bams, bws,  bed, gtfs, locus, refn, roi)
        add_bam(addbam)
        remove_bam(rmbam)
        create_server(port)
    else:
        print_genomelist()
