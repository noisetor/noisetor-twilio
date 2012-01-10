#!/usr/bin/perl
# vi:set ai sw=4 ts=4:

use CGI;
use Text::Wrap;

use strict;
use warnings;

sub rmwhite {
	my $string = shift;
	$string =~ s/^\s+//gm;
	return $string;
}

my $q = new CGI;

# These paramaters appear in both Recordings and Transcripts
my $RecordingUrl = $q->param("RecordingUrl");
my $RecordingSid = $q->param("RecordingSid");
my $Caller = $q->param("Caller");

# These appear only in Recordings
my $RecordingDuration = $q->param("RecordingDuration");
my $CallerCity = $q->param("CallerCity");
my $CallerState = $q->param("CallerState");
my $CallerZip = $q->param("CallerZip");

# These appear only in Transcripts
my $TranscriptionStatus = $q->param("TranscriptionStatus");
my $TranscriptionSid = $q->param("TranscriptionSid");
my $TranscriptionText = $q->param("TranscriptionText");

exit if $TranscriptionStatus and $TranscriptionStatus ne "completed";
$TranscriptionText = wrap("> ", "> ", $TranscriptionText) if $TranscriptionText;

open my $fd, "| /usr/sbin/sendmail -oi -t -fmct"
	or die "fork: $!";

print $fd rmwhite <<"	EOT";
	From: Voicemail <admin\@noisetor.net>
	Subject: New voicemail from $Caller
	To: admin\@noisetor.net
	EOT

unless ($TranscriptionSid) {
	print $fd rmwhite <<"		EOT";
		Message-Id: <$RecordingSid\@voicemail.noisetor.net>

		You have a new $RecordingDuration second long voicemail from $Caller ($CallerCity, $CallerState $CallerZip):

		$RecordingUrl
		EOT
}

else {
	print $fd rmwhite <<"		EOT";
		Message-Id: <$TranscriptionSid\@voicemail.noisetor.net>
		References: <$RecordingSid\@voicemail.noisetor.net>

		Transcript of previously sent voicemail <$RecordingUrl>:

		$TranscriptionText
		EOT
}

print $q->header, rmwhite <<"	EOT";
	<?xml version="1.0" encoding="UTF-8"?>
	<Response>
		<Hangup/>
	</Response>
	EOT
