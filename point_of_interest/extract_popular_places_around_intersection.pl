#!/usr/bin/env perl
use Time::localtime;
use File::Spec::Functions;
use LWP::Simple;
use JSON -convert_blessed_universally;
use JSON::Parse 'json_to_perl';
use Time::HiRes qw(gettimeofday); 

use JSON;
use Data::Dumper;

use HTML::Parser ();
use LWP;
use Mozilla::CA; #for https requests
use List::MoreUtils qw(uniq);

my $browser = LWP::UserAgent->new;

use strict; 
#use warnings;

use Text::CSV; 

my $file = "int_file.csv";
 
open(my $data, '<', $file) or die "Could not open '$file' $!\n";

my @uid_array = ();
my @lon_array = ();
my @lat_array = ();

my $i =0;
while (my $line = <$data>) 
{
  chomp $line;
 
  my @fields = split "," , $line;
  my $uid = $fields[0];
  my $lon = $fields[1];
  my $lat = $fields[2];

  $uid_array[$i] = $uid;
  $lon_array[$i] = $lon;
  $lat_array[$i] = $lat;

  $i = $i + 1;

}

close $file;

my $csv = Text::CSV->new ({
  binary    => 1,
  auto_diag => 1,
  sep_char  => ','    # not really needed as this is the default
});

#open(my $data, '<:encoding(utf8)', $file) or die "Could not open '$file' $!\n";
open (my $OUTFILE, ">washington_intersection_popular_places_250m.csv") or die "$!";

my @list_tokens = ("point_of_interest","establishment","route","park","lodging","store","cafe","restaurant","food","neighborhood",
	"political","clothing_store","real_estate_agency","beauty_salon","jewelry_store","shopping_mall","accounting","finance","bar",
	"book_store","travel_agency","lawyer","dentist","health","spa","hair_care","home_goods_store","night_club","furniture_store",
	"general_contractor","laundry","bakery","shoe_store","art_gallery","museum","pharmacy","bank","meal_takeaway","taxi_stand",
	"transit_station","grocery_or_supermarket","parking","atm","school","church","place_of_worship","meal_delivery","subway_station",
	"train_station","car_wash","electronics_store","liquor_store","florist","insurance_agency","department_store","painter","electrician",
	"hardware_store","veterinary_care","pet_store","local_government_office","police","courthouse","moving_company","locksmith","movie_theater",
	"movie_rental","amusement_park","natural_feature","post_office","library","gym","city_hall","sublocality_level_1","sublocality",
	"convenience_store","doctor","bowling_alley","hospital","university","car_repair","gas_station","bicycle_store","plumber",
	"synagogue","car_dealer","storage","car_rental","fire_station","funeral_home","stadium","zoo","locality","mosque","airport",
	"physiotherapist","embassy","campground","aquarium","casino","hindu_temple");


print $OUTFILE "uid,lat,lon,place_id,name,vicinity,tags,",join(", ", @list_tokens),"\n";

my $radius = 250; #mts

my $count =0;
my @tags_list; 
my $pagetoken;


for (my $j = 0; $j <= 8437; $j += 1)
{

	my $uid = $uid_array[$j];
	my $center_lat = $lat_array[$j];
	my $center_lon = $lon_array[$j];

	my $url_base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=$center_lat,$center_lon&radius=$radius&key=AIzaSyABbJfVrWZs8LTuMMGWpNtDVv27hWAulK8";

	while (1)
	{
		$count = $count + 1;
		my $url = $url_base;
		
		#print "count: ", $count,"\n";

		if(defined($pagetoken)) 
		{
			$url = "$url_base&pagetoken=$pagetoken";
		}

		#print $url,"\n";

		$pagetoken = get_places($uid, $url, $OUTFILE, \@list_tokens);

		last if (!defined($pagetoken));
		sleep 5;

	}

	print "intersection done $uid\n";
	print "--------\n";
}

my @unique_tags = uniq @tags_list;
print Dumper @unique_tags;
print join(", ", @unique_tags),"\n";
if (not $csv->eof) 
{
  $csv->error_diag();
}

close $OUTFILE;


sub get_places 
{	
	my $uid = shift;
	my $url = shift;
	my $OUTFILE = shift;
	my $list_tokens_ref = shift;
		
	my @list_tokens = @{$list_tokens_ref};
	  
	my $response = $browser->get( $url );
	die "Can't get $url -- ", $response->status_line
	unless $response->is_success;
	
	my $text = decode_json($response->content);
	my @text_arr = @{$text->{'results'}};

	#print Dumper $text->{'status'};		

	my $next_page_token = $text->{'next_page_token'};
	#print "places count: ", $#text_arr+1, "\n";	
	
	foreach my $l (@text_arr) 
	{
		my $lat = ${$l}{'geometry'}->{'location'}->{'lat'};
		my $lon = ${$l}{'geometry'}->{'location'}->{'lng'};
		my $tags =  ${$l}{'types'};
		my $place_id =  ${$l}{'place_id'};
		my $name =  ${$l}{'name'};
		$name =~ tr/"/'/; #replace double by single quotes
		my $vicinity =  ${$l}{'vicinity'};		
		$vicinity =~ tr/"/'/; #replace double by single quotes

		my @count_arr = get_count_arr(\@list_tokens,$tags);
		print $OUTFILE "$uid,$lat,$lon,$place_id,\"$name\",\"$vicinity\",",join(" ", @{$tags}),",",join(", ", @count_arr),"\n";		
				
	}
	#print "next_page_token: ", $next_page_token,"\n";
	return($next_page_token);
}


sub get_count_arr 
{
	my $list_tokens_ref = shift;
	my $test_ref = shift;
	
	my @list_tokens = @{$list_tokens_ref};
	my @test = @{$test_ref};
	my %count;


	$count{$_}++ foreach @test;
	my @count_arr;

	push(@count_arr, $count{$_}) foreach @list_tokens;
	return(@count_arr);
}


exit;




















