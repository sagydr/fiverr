import itertools as it
import csv
import sys


class Email(object):
    def __init__(self):
        self.date = None
        self.fromm = None
        self.subject = None
        self.content = ''

    def _clean(self, line, txt_to_remove):
        line = line.replace(txt_to_remove, '').replace('"', '').replace('\n', '')
        return line.strip()

    def add_date(self, date_str):
        self.date = self._clean(date_str, 'Date:')

    def add_subject(self, subject_str):
        self.subject = self._clean(subject_str, 'Subject:')

    def add_from(self, from_str):
        self.fromm = self._clean(from_str, 'From:')

    def add_content_line(self, content_line):
        self.content += content_line.strip()

    def to_arr(self):
        return [self.subject, self.fromm, self.date, self.content]


class EmailParser(object):
    def __init__(self, input_file):
        self.input_file = input_file
        self.all_emails = []

    def parse_file(self):
        found = 0
        with open(self.input_file, 'r') as f:
            for key, group in it.groupby(f, lambda line: line.startswith('=============================')):
                found += 1
                if not key:
                    # print str(found) + ") key = " + str(list(group)[0:10])
                    self.parse_email(group)
                    # group = list(group)
                    # print(group)

    def parse_email(self, email_lines):
        e = Email()
        # print "parsing email"
        content_start = -1
        for idx, email_line in enumerate(email_lines):

            if email_line.startswith('Date:'):
                e.add_date(email_line)
            elif email_line.startswith('From:'):
                e.add_from(email_line)
            elif email_line.startswith('Subject:'):
                e.add_subject(email_line)
            elif email_line.lower().startswith('content-type: text/plain'):
                # print "found content starting at line - ", idx
                content_start = idx
                # when reached here, only the content is found
                break

        if content_start > 0:
            self.extract_content(e, email_lines)
        else:
            print "NO CONTENT FOUND"

        self.all_emails.append(e)

    def extract_content(self, email, email_lines):
        """
        the email_lines reaching this method, are all the lines starting from Content-Type:...
        i.e. not parsing the header lines again
        :param email:
        :param email_lines:
        :return:
        """
        content_lines = list(email_lines)
        count_cl = 0
        # print "extracting content from: ", email, "out of ", len(content_lines)
        for l in content_lines:
            if l.strip().startswith('charset='):
                # print "skipping charset"
                continue
            elif l.strip().startswith(('Content-Type', 'Content-Transfer')):
                # print "skipping Content-Type"
                continue
            elif l.strip().startswith(('------', '-----Original')) or '===' in l.strip():
                # print "found end-of-content line: ", l.strip()
                break
            else:
                count_cl += 1
                # print "adding content - ", count_cl
                email.add_content_line(l)

    def write_to_csv(self):
        output_file = self.input_file+'.csv'
        with open(output_file, 'wb') as csvfile:
            emailcsvwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for e in self.all_emails:
                emailcsvwriter.writerow(e.to_arr())
        print "finished creating CSV: ", output_file

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage:   python csv_email_parser.py <input-file>"
    else:
        input_file = sys.argv[1]
        test = EmailParser(input_file)
        test.parse_file()
        test.write_to_csv()
